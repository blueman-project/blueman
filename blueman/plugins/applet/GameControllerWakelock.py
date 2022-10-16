from gettext import gettext as _
import logging
from typing import Any, Dict, Optional

from blueman.bluez.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gio


class GameControllerWakelock(AppletPlugin):
    __description__ = _("Temporarily suspends the screensaver when a bluetooth game controller is connected.")
    __author__ = "bwRavencl"
    __icon__ = "input-gaming-symbolic"

    def on_load(self) -> None:
        self.cookies: Dict[str, int] = {}
        self._screensaver: Optional[Gio.DBusProxy] = None
        self._screensaver_found: bool = False
        self.watch = Gio.bus_watch_name(
            Gio.BusType.SESSION,
            "org.freedesktop.ScreenSaver",
            Gio.BusNameWatcherFlags.NONE,
            self.on_name_appeared,
            self.on_name_vanished
        )

        self.xfce_watch = Gio.bus_watch_name(
            Gio.BusType.SESSION,
            "org.xfce.ScreenSaver",
            Gio.BusNameWatcherFlags.NONE,
            self.on_name_appeared,
            self.on_name_vanished
        )

    def on_unload(self) -> None:
        if self.watch:
            Gio.bus_unwatch_name(self.watch)

        if self._screensaver is None:
            return

        for path in self.cookies:
            self._remove_lock(path)

    def on_name_appeared(self, connection: Gio.DBusConnection, name: str, owner: str) -> None:
        logging.debug(f"Got name {name} and owner: {owner}")
        if self._screensaver_found:
            assert self._screensaver is not None
            logging.warning(f"Already found ScreenSaver {self._screensaver.get_name()}")
            return

        if name == "org.freedesktop.ScreenSaver":
            self._screensaver = Gio.DBusProxy.new_sync(
                connection,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.freedesktop.ScreenSaver",
                "/org/freedesktop/ScreenSaver",
                "org.freedesktop.ScreenSaver",
                None
            )
            self._screensaver_found = True

        elif name == "org.xfce.ScreenSaver":
            self._screensaver = Gio.DBusProxy.new_sync(
                connection,
                Gio.DBusProxyFlags.NONE,
                None,
                "org.xfce.ScreenSaver",
                "/",
                "org.xfce.ScreenSaver",
                None
            )
            self._screensaver_found = True

    def on_name_vanished(self, _connection: Gio.DBusConnection, name: str) -> None:
        logging.debug(f"ScreenSaver {name} vanished")
        self.cookies = {}
        self.proxy = None

    def _add_lock(self, path: str) -> None:
        if self._screensaver is None:
            logging.debug("Can not inhibit, no screensaver found")
            return

        cookie = self._screensaver.Inhibit("(ss)", "Blueman GamecontrollerWakerlock", "Controller connected")
        if cookie > 0:
            logging.debug(f"Adding lock with cookie: {cookie}")
            self.cookies[path] = cookie

    def _remove_lock(self, path: str) -> None:
        if self._screensaver is None:
            return

        cookie = self.cookies.pop(path, None)
        if cookie is None:
            logging.warning("No inhibit cookie found")
            return

        self._screensaver.UnInhibit("(u)", cookie)
        logging.debug(f"Removing lock for cookie: {cookie}")

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected":
            klass = Device(obj_path=path)["Class"] & 0x1fff

            if klass == 0x504 or klass == 0x508:
                if value:
                    self._add_lock(path)
                else:
                    self._remove_lock(path)
