"""Notice when the Bluetooth controller has stopped responding and reset it on request.

Nothing here resets a controller by itself: detections only produce a verdict, and the
manager offers the reset to the user (or performs it when the user opted in to resetting
whenever Bluetooth is turned on).
"""

import logging
import time
from collections.abc import Callable
from enum import Enum
from gettext import gettext as _
from typing import Protocol

from gi.repository import Gio, GLib, GObject

from blueman.main.AdapterReset import AdapterResetError, KernelFault, hci_name_from_path, parse_kernel_fault, \
    pkexec_command, resolve_binding
from blueman.main.DBusProxies import DBusProxyFailed, Mechanism

KERNEL_LOG_COMMAND = ("journalctl", "--dmesg", "--follow", "--lines=0", "--output=cat", "--no-pager")


class KernelLogWatcher:
    """Follows the kernel log through journalctl and reports controller faults.

    dmesg is restricted to root on many systems, while the journal is readable by members
    of the ``adm``/``systemd-journal`` groups. When neither is available this stays silent
    and the discovery checks remain the only detection.
    """

    def __init__(self, on_fault: Callable[[KernelFault], None]) -> None:
        self._on_fault = on_fault
        self._process: Gio.Subprocess | None = None
        self._stream: Gio.DataInputStream | None = None
        self._cancellable: Gio.Cancellable | None = None

    @property
    def running(self) -> bool:
        return self._process is not None

    def start(self) -> None:
        if self._process is not None:
            return
        try:
            process = Gio.Subprocess.new(
                list(KERNEL_LOG_COMMAND),
                Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE)
        except GLib.Error as e:
            logging.info(f"Kernel log is not available, controller faults will not be detected: {e.message}")
            return
        self._process = process
        self._cancellable = Gio.Cancellable()
        self._stream = Gio.DataInputStream.new(process.get_stdout_pipe())
        self._read_next()

    def stop(self) -> None:
        if self._cancellable is not None:
            self._cancellable.cancel()
        if self._process is not None:
            self._process.force_exit()
        self._process = None
        self._stream = None
        self._cancellable = None

    def _read_next(self) -> None:
        if self._stream is not None:
            self._stream.read_line_async(GLib.PRIORITY_LOW, self._cancellable, self._on_line)

    def _on_line(self, stream: GObject.Object | None, result: Gio.AsyncResult, _data: object = None) -> None:
        assert isinstance(stream, Gio.DataInputStream)
        try:
            line, _length = stream.read_line_finish_utf8(result)
        except GLib.Error as e:
            if self._cancellable is not None and not self._cancellable.is_cancelled():
                logging.info(f"Stopped reading the kernel log: {e.message}")
                self.stop()
            return
        if line is None:
            logging.info("Kernel log reader exited")
            self.stop()
            return
        self.feed(line)
        self._read_next()

    def feed(self, line: str) -> None:
        fault = parse_kernel_fault(line)
        if fault is not None:
            self._on_fault(fault)


class Stall(Enum):
    NOT_STARTED = "not-started"
    SILENT = "silent"


class DiscoveryWatch:
    """Judges whether a discovery session looks stuck.

    ``NOT_STARTED``: BlueZ accepted StartDiscovery but the adapter never reported
    ``Discovering``. ``SILENT``: discovery ran for a while and no device appeared or
    updated its signal. A quiet room produces ``SILENT`` too, so this is only ever a
    suggestion shown to the user.
    """

    START_GRACE_SECONDS = 6
    SILENT_AFTER_SECONDS = 25

    def __init__(self, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._started_at: float | None = None
        self._discovering = False
        self._activity = 0

    @property
    def active(self) -> bool:
        return self._started_at is not None

    def begin(self) -> None:
        self._started_at = self._clock()
        self._discovering = False
        self._activity = 0

    def note_discovering(self, discovering: bool) -> None:
        if discovering:
            self._discovering = True

    def note_activity(self) -> None:
        self._activity += 1

    def end(self) -> None:
        self._started_at = None

    def verdict(self) -> Stall | None:
        if self._started_at is None:
            return None
        elapsed = self._clock() - self._started_at
        if not self._discovering:
            return Stall.NOT_STARTED if elapsed >= self.START_GRACE_SECONDS else None
        if self._activity == 0 and elapsed >= self.SILENT_AFTER_SECONDS:
            return Stall.SILENT
        return None


# The mechanism installed on the system may be older than this checkout and lack
# ResetAdapter, or may not be installed at all; pkexec does the same reset then.
_FALLBACK_ERRORS = frozenset({
    "org.freedesktop.DBus.Error.UnknownMethod",
    "org.freedesktop.DBus.Error.ServiceUnknown",
    "org.freedesktop.DBus.Error.NameHasNoOwner",
})
# pkexec: 126 means the authentication dialog was dismissed, 127 not authorized.
_PKEXEC_DENIED = (126, 127)
# The polkit dialog waits for the user, so the call must outlive D-Bus's 25 s default.
RESET_CALL_TIMEOUT_MS = 180_000

ResetDone = Callable[[bool, str | None], None]
PkexecRunner = Callable[[list[str], Callable[[int, str], None]], None]


def _run_pkexec(argv: list[str], on_exit: Callable[[int, str], None]) -> None:
    try:
        process = Gio.Subprocess.new(argv, Gio.SubprocessFlags.STDERR_PIPE | Gio.SubprocessFlags.STDOUT_SILENCE)
    except GLib.Error as e:
        on_exit(127, e.message)
        return

    def finish(proc: GObject.Object | None, result: Gio.AsyncResult, _data: object = None) -> None:
        assert isinstance(proc, Gio.Subprocess)
        try:
            _ok, _stdout, stderr = proc.communicate_utf8_finish(result)
        except GLib.Error as e:
            on_exit(1, e.message)
            return
        on_exit(proc.get_exit_status(), (stderr or "").strip())

    process.communicate_utf8_async(None, None, finish)


class AdapterResetClient:
    def __init__(self, mechanism_factory: Callable[[], Gio.DBusProxy] = Mechanism,
                 run_pkexec: PkexecRunner = _run_pkexec) -> None:
        self._mechanism_factory = mechanism_factory
        self._run_pkexec = run_pkexec
        self.busy = False

    def reset(self, hci: str, on_done: ResetDone) -> None:
        if self.busy:
            return
        self.busy = True

        def done(ok: bool, message: str | None) -> None:
            self.busy = False
            on_done(ok, message)

        try:
            mechanism = self._mechanism_factory()
        except DBusProxyFailed as e:
            logging.info(f"Mechanism unavailable ({e}), resetting through pkexec")
            self._reset_with_pkexec(hci, done)
            return

        def finish(proxy: Gio.DBusProxy, result: Gio.AsyncResult) -> None:
            try:
                proxy.call_finish(result)
            except GLib.Error as e:
                remote = Gio.DBusError.get_remote_error(e)
                if remote in _FALLBACK_ERRORS:
                    logging.info(f"Mechanism cannot reset adapters ({remote}), using pkexec")
                    self._reset_with_pkexec(hci, done)
                    return
                # strip_remote_error does not reach the Python copy of the message.
                message = e.message.removeprefix(f"GDBus.Error:{remote}: ") if remote else e.message
                # A dismissed or refused polkit prompt is the user's choice, not a failure to report.
                done(False, None if message == "Not authorized" else message)
                return
            done(True, None)

        mechanism.call("ResetAdapter", GLib.Variant("(s)", (hci,)), Gio.DBusCallFlags.NONE,
                       RESET_CALL_TIMEOUT_MS, None, finish)

    def _reset_with_pkexec(self, hci: str, done: ResetDone) -> None:
        try:
            argv = pkexec_command(resolve_binding(hci))
        except AdapterResetError as e:
            done(False, str(e))
            return

        def on_exit(status: int, stderr: str) -> None:
            if status == 0:
                done(True, None)
            elif status in _PKEXEC_DENIED:
                done(False, None)
            else:
                done(False, stderr or f"Reset command exited with status {status}")

        self._run_pkexec(argv, on_exit)


class Notice(Protocol):
    def present(self, title: str, detail: str, action_label: str | None = None,
                action_name: str | None = None, busy: bool = False) -> None:
        ...

    def dismiss(self) -> None:
        ...


RESET_ACTION = "app.reset-adapter"
# Unbinding the driver makes the kernel log its own errors; those are not new faults.
FAULT_QUIET_SECONDS = 20
# How long to wait for the adapter to come back before giving up on powering it on.
POWER_ON_WAIT_SECONDS = 15


class ControllerRecovery:
    """Connects detections to the dashboard notice and runs resets the user asks for."""

    def __init__(
        self,
        notice: Notice,
        adapter_path: Callable[[], str | None],
        connected_count: Callable[[], int],
        set_powered: Callable[[bool], None],
        confirm: Callable[[int, Callable[[], None]], None],
        client: AdapterResetClient | None = None,
        watcher_factory: Callable[[Callable[[KernelFault], None]], KernelLogWatcher] = KernelLogWatcher,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._notice = notice
        self._adapter_path = adapter_path
        self._connected_count = connected_count
        self._set_powered = set_powered
        self._confirm = confirm
        self._client = client or AdapterResetClient()
        self._watcher = watcher_factory(self.on_kernel_fault)
        self._clock = clock
        self.discovery = DiscoveryWatch(clock)
        self._discovery_sources: list[int] = []
        self._last_reset_at: float | None = None
        self._power_on_until: float | None = None
        self._discovery_reported = False

    @property
    def busy(self) -> bool:
        return self._client.busy

    def start(self) -> None:
        self._watcher.start()

    def stop(self) -> None:
        self._watcher.stop()
        self._clear_discovery_checks()

    def _current_hci(self) -> str | None:
        return hci_name_from_path(self._adapter_path())

    def _offer_reset(self, title: str, detail: str) -> None:
        if not self.busy:
            self._notice.present(title, detail, _("Reset Adapter"), RESET_ACTION)

    # Kernel log

    def on_kernel_fault(self, fault: KernelFault) -> None:
        if fault.hci != self._current_hci() or self.busy:
            return
        if self._last_reset_at is not None and self._clock() - self._last_reset_at < FAULT_QUIET_SECONDS:
            return
        self._offer_reset(
            _("Bluetooth adapter stopped responding"),
            _("The kernel reported “%(message)s” for %(adapter)s. Resetting the adapter reloads its driver; "
              "connected devices will disconnect.") % {"message": fault.message, "adapter": fault.hci})

    # Discovery

    def discovery_started(self) -> None:
        self._clear_discovery_checks()
        self._discovery_reported = False
        self.discovery.begin()
        for delay in (DiscoveryWatch.START_GRACE_SECONDS, DiscoveryWatch.SILENT_AFTER_SECONDS):
            self._discovery_sources.append(GLib.timeout_add_seconds(delay, self._check_discovery))

    def discovery_state(self, discovering: bool) -> None:
        self.discovery.note_discovering(discovering)

    def discovery_activity(self) -> None:
        if self.discovery.active:
            self.discovery.note_activity()

    def discovery_finished(self) -> None:
        self._clear_discovery_checks()
        self.discovery.end()

    def discovery_failed(self, message: str) -> None:
        self.discovery_finished()
        self._offer_reset(_("Scanning failed"),
                          _("BlueZ could not start a scan: %s. Resetting the adapter often fixes this.") % message)

    def _check_discovery(self) -> bool:
        if self._discovery_sources:
            self._discovery_sources.pop(0)
        verdict = self.discovery.verdict()
        if verdict is None or self._discovery_reported:
            return False
        self._discovery_reported = True
        if verdict is Stall.NOT_STARTED:
            self._offer_reset(_("Scanning did not start"),
                              _("The adapter accepted the scan but never began searching. "
                                "Resetting the adapter usually fixes this."))
        else:
            self._offer_reset(_("No devices found yet"),
                              _("Nothing has answered the scan. If a device nearby is in pairing mode, "
                                "the controller may be stuck; resetting the adapter usually helps."))
        return False

    def _clear_discovery_checks(self) -> None:
        for source in self._discovery_sources:
            GLib.source_remove(source)
        self._discovery_sources = []

    # Reset

    def request_reset(self) -> None:
        """Reset chosen by the user; asks first when it would drop connections."""
        if self.busy:
            return
        connected = self._connected_count()
        if connected:
            self._confirm(connected, self._reset)
        else:
            self._reset()

    def reset_then_power_on(self) -> None:
        """Opt-in reset when Bluetooth is turned on; Bluetooth ends up on whatever happens."""
        if self.busy or self._current_hci() is None:
            self._set_powered(True)
            return
        self._reset(power_on=True)

    def _reset(self, power_on: bool = False) -> None:
        hci = self._current_hci()
        if hci is None:
            self._notice.present(_("No Bluetooth adapter"), _("There is no adapter to reset."))
            return
        self.discovery_finished()
        self._last_reset_at = self._clock()
        self._notice.present(_("Resetting adapter…"),
                             _("Reloading the driver for %s. Devices reconnect once it is back.") % hci, busy=True)

        def done(ok: bool, message: str | None) -> None:
            self._last_reset_at = self._clock()
            if power_on:
                self._power_on_until = self._clock() + POWER_ON_WAIT_SECONDS
                self._set_powered(True)
            if ok:
                self._notice.dismiss()
            elif message is None:
                self._notice.dismiss()
            else:
                self._notice.present(_("Adapter reset failed"), message, _("Try Again"), RESET_ACTION)

        self._client.reset(hci, done)

    def adapter_added(self, path: str) -> None:
        """The adapter returns as a new D-Bus object after a reset; restore power if wanted."""
        if self._power_on_until is None:
            return
        if self._clock() <= self._power_on_until and hci_name_from_path(path) is not None:
            self._set_powered(True)
        self._power_on_until = None
