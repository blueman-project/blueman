from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus.service
from blueman.bluez.Network import Network
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Mechanism import Mechanism
from blueman.Functions import *


class DhcpClient(AppletPlugin):
    __description__ = _("Provides a basic dhcp client for Bluetooth PAN connections.")
    __icon__ = "network"
    __author__ = "Walmis"

    _any_network = None

    def on_load(self, applet):
        self._any_network = Network()
        self._any_network.connect_signal('property-changed', self._on_network_prop_changed)

        self.quering = []

    def on_unload(self):
        del self._any_network

    @dbus.service.method('org.blueman.Applet', in_signature="s")
    def DhcpClient(self, interface):
        self.dhcp_acquire(interface)

    def _on_network_prop_changed(self, _network, key, value):
        if key == "Interface":
            if value != "":
                self.dhcp_acquire(value)

    def dhcp_acquire(self, device):
        if device not in self.quering:
            self.quering.append(device)
        else:
            return

        if device != "":
            def reply(ip_address):
                Notification(_("Bluetooth Network"),
                             _("Interface %(0)s bound to IP address %(1)s") % {"0": device, "1": ip_address},
                             pixbuf=get_icon("network-workgroup", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)

                self.quering.remove(device)

            def err(msg):
                dprint(msg)
                Notification(_("Bluetooth Network"), _("Failed to obtain an IP address on %s") % (device),
                             pixbuf=get_icon("network-workgroup", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)

                self.quering.remove(device)

            Notification(_("Bluetooth Network"), _("Trying to obtain an IP address on %s\nPlease wait..." % device),
                         pixbuf=get_icon("network-workgroup", 48),
                         status_icon=self.Applet.Plugins.StatusIcon)

            m = Mechanism()
            m.DhcpClient(device, reply_handler=reply, error_handler=err, timeout=120)
