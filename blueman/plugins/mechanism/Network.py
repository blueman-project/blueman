# coding=utf-8

from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler

DHCPDHANDLERS = {"DnsMasqHandler": DnsMasqHandler,
                 "DhcpdHandler": DhcpdHandler,
                 "UdhcpdHandler": UdhcpdHandler}


class Network(MechanismPlugin):
    def on_load(self):
        self.parent.add_method("DhcpClient", ("s",), "s", self._run_dhcp_client, pass_sender=True, is_async=True)
        self.parent.add_method("EnableNetwork", ("s", "s", "s"), "", self._enable_network, pass_sender=True)
        self.parent.add_method("ReloadNetwork", (), "", self._reload_network, pass_sender=True)
        self.parent.add_method("DisableNetwork", (), "", self._disable_network, pass_sender=True)

    def _run_dhcp_client(self, net_interface, caller, ok, err):
        self.timer.stop()

        self.confirm_authorization(caller, "org.blueman.dhcp.client")

        from blueman.main.DhcpClient import DhcpClient

        def dh_error(dh, message, ok, err):
            err(message)
            self.timer.resume()

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

    def _enable_network(self, ip_address, netmask, dhcp_handler, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.set_ipv4(ip_address, netmask)
        nc.set_dhcp_handler(DHCPDHANDLERS[dhcp_handler])
        nc.apply_settings()

    def _reload_network(self, caller):
        nc = NetConf.get_default()
        if nc.ip4_address is None or nc.ip4_mask is None:
            nc.ip4_changed = False
            nc.store()
            return

        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc.apply_settings()

    def _disable_network(self, caller):
        self.confirm_authorization(caller, "org.blueman.network.setup")
        nc = NetConf.get_default()
        nc.remove_settings()
        nc.set_ipv4(None, None)
        nc.store()
