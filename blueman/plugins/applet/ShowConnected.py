from gettext import gettext as _
import logging
from typing import Optional, Any, List

from gi.repository import GLib
from blueman.plugins.AppletPlugin import AppletPlugin
from gettext import ngettext

from blueman.plugins.applet.StatusIcon import StatusIconProvider
from blueman.main.PluginManager import PluginManager


class ShowConnected(AppletPlugin, StatusIconProvider):
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]
    __icon__ = "bluetooth-symbolic"
    __description__ = _("Adds an indication on the status icon when Bluetooth is active and shows the number of "
                        "connections in the tooltip.")

    def on_load(self) -> None:
        self.num_connections = 0
        self.active = False
        self.initialized = False
        self._handlers: List[int] = []
        self._handlers.append(self.parent.Plugins.connect('plugin-loaded', self._on_plugins_changed))
        self._handlers.append(self.parent.Plugins.connect('plugin-unloaded', self._on_plugins_changed))

    def on_unload(self) -> None:
        self.parent.Plugins.StatusIcon.set_tooltip_text(None)
        self.num_connections = 0
        self.parent.Plugins.StatusIcon.icon_should_change()
        for handler in self._handlers:
            self.parent.Plugins.disconnect(handler)
        self._handlers = []

    def on_status_icon_query_icon(self) -> Optional[str]:
        if self.num_connections > 0:
            self.active = True
            return "blueman-active"
        else:
            self.active = False
            return None

    def enumerate_connections(self) -> bool:
        self.num_connections = 0
        for device in self.parent.Manager.get_devices():
            if device["Connected"]:
                self.num_connections += 1

        logging.info("Found %d existing connections" % self.num_connections)
        if (self.num_connections > 0 and not self.active) or \
                (self.num_connections == 0 and self.active):
            self.parent.Plugins.StatusIcon.icon_should_change()

        self.update_statusicon()

        return False

    def update_statusicon(self) -> None:
        if self.num_connections > 0:
            self.parent.Plugins.StatusIcon.set_tooltip_title(_("Bluetooth Active"))
            self.parent.Plugins.StatusIcon.set_tooltip_text(
                ngettext("<b>%(connections)d Active Connection</b>",
                         "<b>%(connections)d Active Connections</b>",
                         self.num_connections) % {"connections": self.num_connections})
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
            self.num_connections = 0
            self.update_statusicon()

    def on_device_property_changed(self, _path: str, key: str, value: Any) -> None:
        if key == "Connected":
            if value:
                self.num_connections += 1
            else:
                self.num_connections -= 1

            if (self.num_connections > 0 and not self.active) or (self.num_connections == 0 and self.active):
                self.parent.Plugins.StatusIcon.icon_should_change()

            self.update_statusicon()

    def on_adapter_added(self, _path: str) -> None:
        self.enumerate_connections()

    def on_adapter_removed(self, _path: str) -> None:
        self.enumerate_connections()

    def _on_plugins_changed(self, _pluginmngr: PluginManager, name: str) -> None:
        if name == "PowerManager":
            self.update_statusicon()
