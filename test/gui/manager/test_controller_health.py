import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk  # noqa: E402

from blueman.gui.manager.ControllerHealth import (  # noqa: E402
    RESET_ACTION,
    AdapterResetClient,
    ControllerRecovery,
    DiscoveryWatch,
    KernelLogWatcher,
    Stall,
)
from blueman.main.AdapterReset import ControllerBinding, KernelFault  # noqa: E402
from blueman.main.DBusProxies import DBusProxyFailed  # noqa: E402


class Clock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


class TestDiscoveryWatch(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = Clock()
        self.watch = DiscoveryWatch(self.clock)

    def test_idle_has_no_verdict(self) -> None:
        self.assertIsNone(self.watch.verdict())

    def test_discovery_that_never_starts(self) -> None:
        self.watch.begin()
        self.clock.now += DiscoveryWatch.START_GRACE_SECONDS - 1
        self.assertIsNone(self.watch.verdict())
        self.clock.now += 1
        self.assertIs(self.watch.verdict(), Stall.NOT_STARTED)

    def test_silent_discovery(self) -> None:
        self.watch.begin()
        self.watch.note_discovering(True)
        self.clock.now += DiscoveryWatch.SILENT_AFTER_SECONDS - 1
        self.assertIsNone(self.watch.verdict())
        self.clock.now += 1
        self.assertIs(self.watch.verdict(), Stall.SILENT)

    def test_activity_clears_suspicion(self) -> None:
        self.watch.begin()
        self.watch.note_discovering(True)
        self.watch.note_activity()
        self.clock.now += DiscoveryWatch.SILENT_AFTER_SECONDS * 2
        self.assertIsNone(self.watch.verdict())

    def test_ended_session_is_not_judged(self) -> None:
        self.watch.begin()
        self.clock.now += 60
        self.watch.end()
        self.assertIsNone(self.watch.verdict())


class TestKernelLogWatcher(unittest.TestCase):
    def test_feed_reports_faults_only(self) -> None:
        on_fault = Mock()
        watcher = KernelLogWatcher(on_fault)
        watcher.feed("Bluetooth: hci0: Intel BT fw patch 0x43 completed & activated")
        on_fault.assert_not_called()
        watcher.feed("Bluetooth: hci0: command 0x0c1a tx timeout")
        on_fault.assert_called_once_with(KernelFault("hci0", "command 0x0c1a tx timeout"))

    def test_missing_journalctl_is_quiet(self) -> None:
        watcher = KernelLogWatcher(Mock())
        with patch("blueman.gui.manager.ControllerHealth.KERNEL_LOG_COMMAND", ("/nonexistent/journalctl",)):
            watcher.start()
        self.assertFalse(watcher.running)
        watcher.stop()


class FakeMechanism:
    def __init__(self, error: tuple[str, str] | None = None) -> None:
        self.error = error
        self.calls: list[tuple[str, object]] = []

    def call(self, name, params, _flags, _timeout, _cancellable, finish) -> None:  # type: ignore[no-untyped-def]
        self.calls.append((name, params.unpack()))
        finish(self, None)

    def call_finish(self, _result: object) -> None:
        if self.error is not None:
            raise Gio.DBusError.new_for_dbus_error(*self.error)


BINDING = ControllerBinding("hci0", "1-9:1.0", Path("/sys/bus/usb/drivers/btusb"), "btusb")


class TestAdapterResetClient(unittest.TestCase):
    def test_mechanism_success(self) -> None:
        mechanism = FakeMechanism()
        done = Mock()
        client = AdapterResetClient(lambda: mechanism, Mock())
        client.reset("hci0", done)
        self.assertEqual(mechanism.calls, [("ResetAdapter", ("hci0",))])
        done.assert_called_once_with(True, None)
        self.assertFalse(client.busy)

    def test_mechanism_failure_is_reported(self) -> None:
        mechanism = FakeMechanism(("org.blueman.Error.AdapterResetFailed", "hci0 has no device in sysfs"))
        done = Mock()
        AdapterResetClient(lambda: mechanism, Mock()).reset("hci0", done)
        done.assert_called_once_with(False, "hci0 has no device in sysfs")

    def test_refused_authorization_is_silent(self) -> None:
        mechanism = FakeMechanism(("org.blueman.Error", "Not authorized"))
        done = Mock()
        AdapterResetClient(lambda: mechanism, Mock()).reset("hci0", done)
        done.assert_called_once_with(False, None)

    def _pkexec_fallback(self, mechanism_factory, status: int, stderr: str = "") -> Mock:  # type: ignore
        run = Mock(side_effect=lambda argv, on_exit: on_exit(status, stderr))
        done = Mock()
        with patch("blueman.gui.manager.ControllerHealth.resolve_binding", return_value=BINDING):
            AdapterResetClient(mechanism_factory, run).reset("hci0", done)
        self.assertEqual(run.call_args.args[0][0], "pkexec")
        return done

    def test_old_mechanism_falls_back_to_pkexec(self) -> None:
        mechanism = FakeMechanism(("org.freedesktop.DBus.Error.UnknownMethod", "No such method"))
        self._pkexec_fallback(lambda: mechanism, 0).assert_called_once_with(True, None)

    def test_missing_mechanism_falls_back_to_pkexec(self) -> None:
        def unavailable() -> None:
            raise DBusProxyFailed("no mechanism")
        self._pkexec_fallback(unavailable, 0).assert_called_once_with(True, None)

    def test_dismissed_pkexec_prompt_is_silent(self) -> None:
        mechanism = FakeMechanism(("org.freedesktop.DBus.Error.ServiceUnknown", "gone"))
        self._pkexec_fallback(lambda: mechanism, 126).assert_called_once_with(False, None)

    def test_pkexec_failure_reports_stderr(self) -> None:
        mechanism = FakeMechanism(("org.freedesktop.DBus.Error.UnknownMethod", "No such method"))
        done = self._pkexec_fallback(lambda: mechanism, 1, "modprobe: FATAL: Module btusb is in use.")
        done.assert_called_once_with(False, "modprobe: FATAL: Module btusb is in use.")


class FakeClient:
    def __init__(self) -> None:
        self.busy = False
        self.pending: list[tuple[str, object]] = []

    def reset(self, hci: str, on_done) -> None:  # type: ignore[no-untyped-def]
        self.busy = True
        self.pending.append((hci, on_done))

    def finish(self, ok: bool, message: str | None = None) -> None:
        _hci, on_done = self.pending.pop()
        self.busy = False
        on_done(ok, message)  # type: ignore[operator]


class TestControllerRecovery(unittest.TestCase):
    def setUp(self) -> None:
        self.notice = Mock()
        self.client = FakeClient()
        self.clock = Clock()
        self.connected = 0
        self.adapter: str | None = "/org/bluez/hci0"
        self.set_powered = Mock()
        self.confirm = Mock()
        self.recovery = ControllerRecovery(
            self.notice,
            adapter_path=lambda: self.adapter,
            connected_count=lambda: self.connected,
            set_powered=self.set_powered,
            confirm=self.confirm,
            client=self.client,  # type: ignore[arg-type]
            watcher_factory=lambda on_fault: Mock(),
            clock=self.clock,
        )

    def test_kernel_fault_offers_reset(self) -> None:
        self.recovery.on_kernel_fault(KernelFault("hci0", "command 0x0c1a tx timeout"))
        self.notice.present.assert_called_once()
        args = self.notice.present.call_args.args
        self.assertIn("command 0x0c1a tx timeout", args[1])
        self.assertEqual(args[3], RESET_ACTION)

    def test_fault_on_other_adapter_is_ignored(self) -> None:
        self.recovery.on_kernel_fault(KernelFault("hci1", "command 0x0c1a tx timeout"))
        self.notice.present.assert_not_called()

    def test_faults_logged_by_our_own_reset_are_ignored(self) -> None:
        self.recovery.request_reset()
        self.client.finish(True)
        self.notice.reset_mock()
        self.clock.now += 5
        self.recovery.on_kernel_fault(KernelFault("hci0", "Resetting usb device"))
        self.notice.present.assert_not_called()
        self.clock.now += 60
        self.recovery.on_kernel_fault(KernelFault("hci0", "command 0x0c1a tx timeout"))
        self.notice.present.assert_called_once()

    def test_reset_without_connections_runs_immediately(self) -> None:
        self.recovery.request_reset()
        self.confirm.assert_not_called()
        self.assertEqual(self.client.pending[0][0], "hci0")
        self.assertTrue(self.notice.present.call_args.kwargs["busy"])
        self.client.finish(True)
        self.notice.dismiss.assert_called_once()
        self.set_powered.assert_not_called()

    def test_reset_with_connections_asks_first(self) -> None:
        self.connected = 2
        self.recovery.request_reset()
        self.assertEqual(self.client.pending, [])
        count, proceed = self.confirm.call_args.args
        self.assertEqual(count, 2)
        proceed()
        self.assertEqual(len(self.client.pending), 1)

    def test_failed_reset_offers_retry(self) -> None:
        self.recovery.request_reset()
        self.client.finish(False, "Could not reload btusb")
        title, detail, label, action = self.notice.present.call_args.args
        self.assertEqual(detail, "Could not reload btusb")
        self.assertEqual(action, RESET_ACTION)

    def test_cancelled_reset_dismisses(self) -> None:
        self.recovery.request_reset()
        self.client.finish(False, None)
        self.notice.dismiss.assert_called_once()

    def test_power_on_resets_then_powers_and_repowers_returning_adapter(self) -> None:
        self.recovery.reset_then_power_on()
        self.set_powered.assert_not_called()
        self.client.finish(True)
        self.set_powered.assert_called_once_with(True)
        self.recovery.adapter_added("/org/bluez/hci0")
        self.assertEqual(self.set_powered.call_count, 2)
        self.recovery.adapter_added("/org/bluez/hci0")
        self.assertEqual(self.set_powered.call_count, 2)

    def test_power_on_still_powers_when_reset_fails(self) -> None:
        self.recovery.reset_then_power_on()
        self.client.finish(False, "boom")
        self.set_powered.assert_called_once_with(True)

    def test_power_on_without_adapter_just_powers(self) -> None:
        self.adapter = None
        self.recovery.reset_then_power_on()
        self.set_powered.assert_called_once_with(True)
        self.assertEqual(self.client.pending, [])

    def test_discovery_stall_offers_reset_once(self) -> None:
        self.recovery.discovery_started()
        self.clock.now += DiscoveryWatch.START_GRACE_SECONDS
        self.recovery._check_discovery()
        self.clock.now += DiscoveryWatch.SILENT_AFTER_SECONDS
        self.recovery._check_discovery()
        self.notice.present.assert_called_once()
        self.recovery.discovery_finished()

    def test_discovery_with_activity_is_quiet(self) -> None:
        self.recovery.discovery_started()
        self.recovery.discovery_state(True)
        self.recovery.discovery_activity()
        self.clock.now += DiscoveryWatch.SILENT_AFTER_SECONDS
        self.recovery._check_discovery()
        self.notice.present.assert_not_called()
        self.recovery.discovery_finished()

    def test_discovery_error_offers_reset(self) -> None:
        self.recovery.discovery_failed("org.bluez.Error.NotReady: Resource Not Ready")
        self.assertEqual(self.notice.present.call_args.args[3], RESET_ACTION)


@unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
class TestControllerNotice(unittest.TestCase):
    def test_present_and_dismiss(self) -> None:
        from blueman.gui.manager.ManagerWindow import ControllerNotice
        notice = ControllerNotice()
        self.assertFalse(notice.shown)
        notice.present("Title", "Detail", "Reset Adapter", RESET_ACTION)
        self.assertTrue(notice.shown)
        self.assertTrue(notice.action_button.get_visible())
        self.assertEqual(notice.action_button.get_action_name(), RESET_ACTION)
        notice.present("Resetting", "…", busy=True)
        self.assertFalse(notice.action_button.get_visible())
        self.assertFalse(notice.close_button.get_visible())
        self.assertTrue(notice.spinner.get_visible())
        notice.dismiss()
        self.assertFalse(notice.shown)
        notice.destroy()


if __name__ == "__main__":
    unittest.main()
