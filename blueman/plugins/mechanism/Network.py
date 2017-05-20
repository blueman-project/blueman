# coding=utf-8
import dbus.service
from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
import subprocess
from gi.repository import GObject
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler

DHCPDHANDLERS = {"DnsMasqHandler": DnsMasqHandler,
                 "DhcpdHandler": DhcpdHandler,
                 "UdhcpdHandler": UdhcpdHandler}


class Network(MechanismPlugin):
    @dbus.service.method('org.blueman.Mechanism', in_signature="s", out_signature="s", sender_keyword="caller",
                         async_callbacks=("ok", "err"))
    def DhcpClient(self, net_interface, caller, ok, err):
        self.timer.stop()

        self.confirm_authorization(caller, "org.blueman.dhcp.client")

        from blueman.main.DhcpClient import DhcpClient

        def dh_error(dh, message, ok, err):
            err(message)
            resume = self.timer.resume()

        def dh_connected(dh, ip, ok, err):
            ok(ip)
            self.timer.resume()

        dh = DhcpClient(net_interface)
        dh.connect("error-occurred", dh_error, ok, err)
        dh.connect("connected", dh_connected, ok, err)
        try:
            dh.run()
        except Exception as e:
            err(e)

    @dbus.service.method('org.blueman.Mechanism', in_signature="ayays", out_signature="", sender_keyword="caller",
                         byte_arrays=True)
    def EnableNetwork(self, ip_address, netmask, dhcp_handler, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.set_ipv4(ip_address, netmask)
        nc.set_dhcp_handler(DHCPDHANDLERS[dhcp_handler])
        nc.apply_settings()

    @dbus.service.method('org.blueman.Mechanism', in_signature="", out_signature="", sender_keyword="caller")
    def ReloadNetwork(self, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.apply_settings()

    @dbus.service.method('org.blueman.Mechanism', in_signature="", out_signature="", sender_keyword="caller")
    def DisableNetwork(self, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.remove_settings()
        nc.set_ipv4(None, None)
        nc.store()
