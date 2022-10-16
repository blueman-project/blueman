from gettext import gettext as _
import logging
from typing import Any, Dict

from blueman.bluez.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GameControllerWakelock(AppletPlugin):
    __description__ = _("Temporarily suspends the screensaver when a bluetooth game controller is connected.")
    __author__ = "bwRavencl"
    __icon__ = "input-gaming-symbolic"

    def on_load(self) -> None:
        self.cookies: Dict[str, int] = {}

    def on_unload(self) -> None:
        for path, cookie in self.cookies.items():
            self.parent.uninhibit(cookie)
        self.cookies = {}

    def _is_contoller(self, device: Device) -> bool:
        klass = device["Class"] & 0x1fff
        if klass == 0x504 or klass == 0x508:
            return True
        return False

    def _add_lock(self, path: str) -> None:
        if path in self.cookies:
            logging.warning(f"Cookie already exists for {path}")
            return

        c = self.parent.inhibit(None, Gtk.ApplicationInhibitFlags.IDLE, "Blueman Gamecontroller Wakelock")
        if c > 0:
            self.cookies[path] = c
            logging.debug(f"Inhibit success {c}")
        else:
            logging.warning("Inhibit failed")

    def _remove_lock(self, path: str) -> None:
        c = self.cookies.pop(path, None)
        if c is not None:
            self.parent.uninhibit(c)
            logging.debug(f"Inhibit removed {c}")
        else:
            logging.warning("No cookies found")

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected" and self._is_contoller(Device(obj_path=path)):
            if value:
                self._add_lock(path)
            else:
                self._remove_lock(path)
