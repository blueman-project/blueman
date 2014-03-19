from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Mechanism import Mechanism
from blueman.main.SignalTracker import SignalTracker
from blueman.Functions import *
import dbus


class DhcpClient(AppletPlugin):
    __description__ = _("Provides a basic dhcp client for Bluetooth PAN connections.")
    __icon__ = "network"
    __author__ = "Walmis"

    def on_load(self, applet):
        self.Signals = SignalTracker()

        self.add_dbus_method(self.DhcpClient, in_signature="s")

        self.Signals.Handle("dbus", dbus.SystemBus(),
                            self.on_network_prop_changed,
                            "PropertyChanged",
                            "org.bluez.Network",
                            path_keyword="path")

        self.quering = []

    def on_unload(self):
        self.Signals.DisconnectAll()

    def DhcpClient(self, interface):
        self.dhcp_acquire(interface)

    def on_network_prop_changed(self, key, value, path):
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
                             pixbuf=get_icon("gtk-network", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)

                self.quering.remove(device)

            def err(msg):
                dprint(msg)
                Notification(_("Bluetooth Network"), _("Failed to obtain an IP address on %s") % (device),
                             pixbuf=get_icon("gtk-network", 48),
                             status_icon=self.Applet.Plugins.StatusIcon)

                self.quering.remove(device)

            Notification(_("Bluetooth Network"), _("Trying to obtain an IP address on %s\nPlease wait..." % device),
                         pixbuf=get_icon("gtk-network", 48),
                         status_icon=self.Applet.Plugins.StatusIcon)

            m = Mechanism()
            m.DhcpClient(device, reply_handler=reply, error_handler=err, timeout=120)
