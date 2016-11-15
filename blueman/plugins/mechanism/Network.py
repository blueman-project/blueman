# coding=utf-8
from blueman.main.DBusServiceObject import *
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler
from socket import inet_aton

DHCPDHANDLERS = {"DnsMasqHandler": DnsMasqHandler,
                 "DhcpdHandler": DhcpdHandler,
                 "UdhcpdHandler": UdhcpdHandler}


class Network(MechanismPlugin):
    @dbus_method('org.blueman.Mechanism', in_signature="s", out_signature="s", invocation_keyword="invocation")
    def DhcpClient(self, net_interface, invocation):
        self.timer.stop()

        self.confirm_authorization(invocation.sender, "org.blueman.dhcp.client")

        from blueman.main.DhcpClient import DhcpClient

        def dh_error(dh, message, return_error):
            return_error(message)
            self.timer.resume()

        def dh_connected(dh, ip, return_value):
            return_value(ip)
            self.timer.resume()

        dh = DhcpClient(net_interface)
        dh.connect("error-occurred", dh_error, invocation.retuen_error)
        dh.connect("connected", dh_connected, invocation.return_value)
        dh.run()

    @dbus_method('org.blueman.Mechanism', in_signature="sss", out_signature="", invocation_keyword="invocation")
    def EnableNetwork(self, ip_address, netmask, dhcp_handler, invocation):
        self.confirm_authorization(invocation.sender, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.set_ipv4(inet_aton(ip_address), inet_aton(netmask))
        nc.set_dhcp_handler(DHCPDHANDLERS[dhcp_handler])
        nc.apply_settings()
        invocation.return_value(None)

    @dbus_method('org.blueman.Mechanism', in_signature="", out_signature="", invocation_keyword="invocation")
    def ReloadNetwork(self, invocation):
        self.confirm_authorization(invocation.sender, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.apply_settings()
        invocation.return_value(None)

    @dbus_method('org.blueman.Mechanism', in_signature="", out_signature="", invocation_keyword="invocation")
    def DisableNetwork(self, invocation):
        self.confirm_authorization(invocation.sender, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.remove_settings()
        nc.set_ipv4(None, None)
        nc.store()
        invocation.return_value(None)
