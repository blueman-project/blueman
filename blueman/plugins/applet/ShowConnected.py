# coding=utf-8
import logging
from gi.repository import GLib
from blueman.plugins.AppletPlugin import AppletPlugin
from gettext import ngettext


class ShowConnected(AppletPlugin):
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]
    __icon__ = "blueman-active"
    __description__ = _("Adds an indication on the status icon when Bluetooth is active and shows the number of "
                        "connections in the tooltip.")

    def on_load(self):
        self.num_connections = 0
        self.active = False
        self.initialized = False

    def on_unload(self):
        self.parent.Plugins.StatusIcon.set_text_line(1, None)
        self.num_connections = 0
        self.parent.Plugins.StatusIcon.icon_should_change()

    def on_status_icon_query_icon(self):
        if self.num_connections > 0:
            self.active = True
            return "blueman-active",
        else:
            self.active = False

    def enumerate_connections(self):
        self.num_connections = 0
        for device in self.parent.Manager.get_devices():
            if device["Connected"]:
                self.num_connections += 1

        logging.info("Found %d existing connections" % self.num_connections)
        if (self.num_connections > 0 and not self.active) or \
                (self.num_connections == 0 and self.active):
            self.parent.Plugins.StatusIcon.icon_should_change()

        self.update_statusicon()

    def update_statusicon(self):
        if self.num_connections > 0:
            self.parent.Plugins.StatusIcon.set_text_line(0, _("Bluetooth Active"))
            self.parent.Plugins.StatusIcon.set_text_line(1, ngettext("<b>%d Active Connection</b>",
                                                                     "<b>%d Active Connections</b>",
                                                                     self.num_connections) % self.num_connections)
        else:
            # bluetooth should be always enabled if powermanager is not loaded
            status = True
            if 'PowerManager' in self.parent.Plugins.get_loaded():
                status = self.parent.Plugins.PowerManager.get_bluetooth_status()

            if status:
                self.parent.Plugins.StatusIcon.set_text_line(0, _("Bluetooth Enabled"))
            else:
                self.parent.Plugins.StatusIcon.set_text_line(0, _("Bluetooth Enabled"))

    def on_manager_state_changed(self, state):
        if state:
            if not self.initialized:
                GLib.timeout_add(0, self.enumerate_connections)
                self.initialized = True
            else:
                GLib.timeout_add(1000, self.enumerate_connections)
        else:
            self.num_connections = 0
            self.update_statusicon()

    def on_device_property_changed(self, _path, key, value):
        if key == "Connected":
            if value:
                self.num_connections += 1
            else:
                self.num_connections -= 1

            if (self.num_connections > 0 and not self.active) or (self.num_connections == 0 and self.active):
                self.parent.Plugins.StatusIcon.icon_should_change()

            self.update_statusicon()

    def on_adapter_added(self, adapter):
        self.enumerate_connections()

    def on_adapter_removed(self, adapter):
        self.enumerate_connections()
