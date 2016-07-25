# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.DBusServiceObject import *
from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
import subprocess
from gi.repository import GObject
from gi.repository import GLib
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler

DHCPDHANDLERS = {"DnsMasqHandler": DnsMasqHandler,
                 "DhcpdHandler": DhcpdHandler,
                 "UdhcpdHandler": UdhcpdHandler}


class Network(MechanismPlugin):
    @dbus_method('org.blueman.Mechanism', in_signature="s", out_signature="s", sender="caller")
    def DhcpClient(self, net_interface, caller):
        self.timer.stop()

        self.confirm_authorization(caller, "org.blueman.dhcp.client")

        from blueman.main.DhcpClient import DhcpClient

        def dh_error(dh, message):
            raise GLib.Error(message)
            resume = self.timer.resume()

        def dh_connected(dh, ip):
            return ip
            self.timer.resume()

        dh = DhcpClient(net_interface)
        dh.connect("error-occurred", dh_error)
        dh.connect("connected", dh_connected)
        dh.run()

    @dbus_method('org.blueman.Mechanism', in_signature="ayays", out_signature="", sender="caller")
    def EnableNetwork(self, ip_address, netmask, dhcp_handler, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.set_ipv4(ip_address, netmask)
        nc.set_dhcp_handler(DHCPDHANDLERS[dhcp_handler])
        nc.apply_settings()

    @dbus_method('org.blueman.Mechanism', in_signature="", out_signature="", sender="caller")
    def ReloadNetwork(self, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.apply_settings()

    @dbus_method('org.blueman.Mechanism', in_signature="", out_signature="", sender="caller")
    def DisableNetwork(self, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.remove_settings()
        nc.set_ipv4(None, None)
        nc.store()
