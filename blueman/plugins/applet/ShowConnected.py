from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
import dbus

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.SignalTracker import SignalTracker
import blueman.bluez as bluez


class ShowConnected(AppletPlugin):
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]
    __icon__ = "blueman-active"
    __description__ = _(
        "Adds an indication on the status icon when Bluetooth is active and shows the number of connections in the tooltip.")

    def on_load(self, applet):
        self.num_connections = 0
        self.active = False
        self.initialized = False

        self.signals = SignalTracker()
        self.signals.Handle('bluez', bluez.Device(), self.on_device_property_changed, 'PropertyChanged')

    def on_unload(self):
        self.signals.DisconnectAll()
        self.Applet.Plugins.StatusIcon.SetTextLine(1, None)
        self.num_connections = 0
        self.Applet.Plugins.StatusIcon.IconShouldChange()


    def on_status_icon_query_icon(self):
        if self.num_connections > 0:
            self.active = True
            #			x_size = int(pixbuf.props.height)
            #			x = get_icon("blueman-txrx", x_size)
            #			pixbuf = composite_icon(pixbuf,
            #				[(x, pixbuf.props.height - x_size, 0, 255)])
            #
            #			return pixbuf
            return ("blueman-active",)
        else:
            self.active = False

    def enumerate_connections(self):
        self.num_connections = 0
        adapters = self.Applet.Manager.list_adapters()
        for adapter in adapters:
            devices = adapter.list_devices()
            for device in devices:
                props = device.get_properties()
                if "Connected" in props:
                    if props["Connected"]:
                        self.num_connections += 1

        dprint("Found %d existing connections" % self.num_connections)
        if (self.num_connections > 0 and not self.active) or \
                (self.num_connections == 0 and self.active):
            self.Applet.Plugins.StatusIcon.IconShouldChange()

        self.update_statusicon()

    def update_statusicon(self):
        if self.num_connections > 0:
            self.Applet.Plugins.StatusIcon.SetTextLine(0,
                                                       _("Bluetooth Active"))
            self.Applet.Plugins.StatusIcon.SetTextLine(1,
                                                       ngettext("<b>%d Active Connection</b>",
                                                                "<b>%d Active Connections</b>",
                                                                self.num_connections) % self.num_connections)
        else:
            self.Applet.Plugins.StatusIcon.SetTextLine(1, None)
            try:
                if self.Applet.Plugins.PowerManager.GetBluetoothStatus():
                    self.Applet.Plugins.StatusIcon.SetTextLine(0,
                                                               _("Bluetooth Enabled"))
            except:
                #bluetooth should be always enabled if powermanager is
                #not loaded
                self.Applet.Plugins.StatusIcon.SetTextLine(0,
                                                           _("Bluetooth Enabled"))

    def on_manager_state_changed(self, state):
        if state:
            if not self.initialized:
                GObject.timeout_add(0, self.enumerate_connections)
                self.initialized = True
            else:
                GObject.timeout_add(1000,
                                    self.enumerate_connections)
        else:
            self.num_connections = 0
            self.update_statusicon()

    def on_device_property_changed(self, key, value):
        if key == "Connected":
            if value:
                self.num_connections += 1
            else:
                self.num_connections -= 1

            if (self.num_connections > 0 and not self.active) or \
                    (self.num_connections == 0 and self.active):
                self.Applet.Plugins.StatusIcon.IconShouldChange()

            self.update_statusicon()

    def on_adapter_added(self, adapter):
        self.enumerate_connections()

    def on_adapter_removed(self, adapter):
        self.enumerate_connections()
