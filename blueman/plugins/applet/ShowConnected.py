from gettext import gettext as _
import logging
from typing import Optional, Any, List, Set

from gi.repository import GLib

from blueman.bluez.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin

from blueman.plugins.applet.StatusIcon import StatusIconProvider
from blueman.main.PluginManager import PluginManager


class ShowConnected(AppletPlugin, StatusIconProvider):
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]
    __icon__ = "bluetooth-symbolic"
    __description__ = _("Adds an indication on the status icon when Bluetooth is active and shows the "
                        "connections in the tooltip.")

    def on_load(self) -> None:
        self._connections: Set[str] = set()
        self.active = False
        self.initialized = False
        self._handlers: List[int] = []
        self._handlers.append(self.parent.Plugins.connect('plugin-loaded', self._on_plugins_changed))
        self._handlers.append(self.parent.Plugins.connect('plugin-unloaded', self._on_plugins_changed))

    def on_unload(self) -> None:
        self.parent.Plugins.StatusIcon.set_tooltip_text(None)
        self._connections = set()
        self.parent.Plugins.StatusIcon.icon_should_change()
        for handler in self._handlers:
            self.parent.Plugins.disconnect(handler)
        self._handlers = []

    def on_status_icon_query_icon(self) -> Optional[str]:
        if self._connections:
            self.active = True
            return "blueman-active"
        else:
            self.active = False
            return None

    def enumerate_connections(self) -> bool:
        self._connections = {device["Alias"] for device in self.parent.Manager.get_devices() if device["Connected"]}

        logging.info(f"Found {len(self._connections):d} existing connections")
        if (self._connections and not self.active) or (not self._connections and self.active):
            self.parent.Plugins.StatusIcon.icon_should_change()

        self.update_statusicon()

        return False

    def update_statusicon(self) -> None:
        if self._connections:
            self.parent.Plugins.StatusIcon.set_tooltip_title(_("Bluetooth Active"))
            self.parent.Plugins.StatusIcon.set_tooltip_text("\n".join(self._connections))
        else:
            self.parent.Plugins.StatusIcon.set_tooltip_text(None)
            if 'PowerManager' in self.parent.Plugins.get_loaded():
                status = self.parent.Plugins.PowerManager.get_bluetooth_status()
                if status:
                    self.parent.Plugins.StatusIcon.set_tooltip_title(_("Bluetooth Enabled"))
                else:
                    self.parent.Plugins.StatusIcon.set_tooltip_title(_("Bluetooth Disabled"))
            else:
                self.parent.Plugins.StatusIcon.set_tooltip_title("Blueman")

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            if not self.initialized:
                GLib.timeout_add(0, self.enumerate_connections)
                self.initialized = True
            else:
                GLib.timeout_add(1000, self.enumerate_connections)
        else:
            self._connections = set()
            self.update_statusicon()

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected":
            name = Device(obj_path=path)["Alias"]

            if value:
                self._connections.add(name)
            else:
                self._connections.remove(name)

            if (self._connections and not self.active) or (self._connections and self.active):
                self.parent.Plugins.StatusIcon.icon_should_change()

            self.update_statusicon()

    def on_adapter_added(self, _path: str) -> None:
        self.enumerate_connections()

    def on_adapter_removed(self, _path: str) -> None:
        self.enumerate_connections()

    def _on_plugins_changed(self, _pluginmngr: PluginManager, name: str) -> None:
        if name == "PowerManager":
            self.update_statusicon()
