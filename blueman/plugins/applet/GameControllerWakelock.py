from gettext import gettext as _
import logging
from typing import Any, Optional

from blueman.bluez.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gio, GLib


class GameControllerWakelock(AppletPlugin):
    __description__ = _("Temporarily suspends the screensaver when a bluetooth game controller is connected.")
    __author__ = "bwRavencl"
    __icon__ = "input-gaming-symbolic"

    def on_load(self) -> None:
        self.__locks: int = 0
        self._inhibit_request: Optional[str] = None
        self._portal_inhibit: Optional[Gio.DBusProxy] = None
        self.watch = Gio.bus_watch_name(
            Gio.BusType.SESSION,
            "org.freedesktop.portal.Desktop",
            Gio.BusNameWatcherFlags.NONE,
            self._on_name_appeared,
            self._on_name_vanished
        )

    def on_unload(self) -> None:
        self.__cleanup()

    def __cleanup(self) -> None:
        if self._inhibit_request:
            self._remove_lock(force=True)

        if self._portal_inhibit is not None:
            self._portal_inhibit.destroy()
            self._portal_inhibit = None

    def _on_name_appeared(self, connection: Gio.DBusConnection, name: str, owner: str) -> None:
        logging.debug(f"Got name {name} and owner: {owner}")
        self._portal_inhibit = Gio.DBusProxy.new_sync(
            connection,
            Gio.DBusProxyFlags.NONE,
            None,
            "org.freedesktop.portal.Desktop",
            "/org/freedesktop/portal/desktop",
            "org.freedesktop.portal.Inhibit",
            None
        )

    def _on_name_vanished(self, _connection: Gio.DBusConnection, name: str) -> None:
        logging.debug(f"ScreenSaver {name} vanished")
        self.__cleanup()

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected":
            klass = Device(obj_path=path)["Class"] & 0x1fff

            if klass == 0x504 or klass == 0x508:
                if value:
                    self._add_lock()
                else:
                    self._remove_lock()

    def _add_lock(self) -> None:
        if self.__locks > 0:
            self.__locks += 1
        else:
            assert self._portal_inhibit is not None
            reason = GLib.Variant("s", "Gamecontroller")
            request_path = self._portal_inhibit.Inhibit("(sua{sv})", "blueman-applet", 8, {"reason": reason})
            logging.debug(request_path)
            if request_path:
                self.__locks += 1
                self._inhibit_request = request_path

        logging.debug(f"Adding lock, total {self.__locks}")

    def _remove_lock(self, force: bool = False) -> None:
        if self._inhibit_request is None:
            logging.warning("No inhibit request found")
            self.__locks = 0
            return

        if self.__locks == 1 or force:
            proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.portal.Desktop",
                self._inhibit_request,
                "org.freedesktop.portal.Request",
                None
            )
            proxy.Close()
            proxy.destroy()
            self.__locks -= 1

            # We should have no locks remaining
            assert self.__locks == 0
        else:
            self.__locks -= 1

        logging.debug(f"Removed lock, total {self.__locks}")
