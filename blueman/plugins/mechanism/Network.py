from typing import Callable, Union, Dict, Type, TYPE_CHECKING
from blueman.bluemantyping import ObjectPath

from blueman.bluez.Network import Network as BluezNetwork
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler, UdhcpdHandler

if TYPE_CHECKING:
    from blueman.main.NetConf import DHCPHandler

DHCPDHANDLERS: Dict[str, Type["DHCPHandler"]] = {
    "DnsMasqHandler": DnsMasqHandler,
    "DhcpdHandler": DhcpdHandler,
    "UdhcpdHandler": UdhcpdHandler
}


class Network(MechanismPlugin):
    def on_load(self) -> None:
        self.parent.add_method("DhcpClient", ("s",), "s", self._run_dhcp_client, pass_sender=True, is_async=True)
        self.parent.add_method("EnableNetwork", ("s", "s", "s", "b"), "", self._enable_network, pass_sender=True)
        self.parent.add_method("DisableNetwork", (), "", self._disable_network, pass_sender=True)

    def _run_dhcp_client(self, object_path: ObjectPath, caller: str, ok: Callable[[str], None],
                         err: Callable[[Union[Exception, int]], None]) -> None:
        self.timer.stop()

        self.confirm_authorization(caller, "org.blueman.dhcp.client")

        from blueman.main.DhcpClient import DhcpClient

        def dh_error(_dh: DhcpClient, num: int) -> None:
            err(num)
            self.timer.resume()

        def dh_connected(_dh: DhcpClient, ip: str) -> None:
            ok(ip)
            self.timer.resume()

        dh = DhcpClient(BluezNetwork(obj_path=object_path)["Interface"])
        dh.connect("error-occurred", dh_error)
        dh.connect("connected", dh_connected)
        try:
            dh.run()
        except Exception as e:
            err(e)

    def _enable_network(self, ip_address: str, netmask: str, dhcp_handler: str, address_changed: bool,
                        caller: str) -> None:
        self.confirm_authorization(caller, "org.blueman.network.setup")
        NetConf.apply_settings(ip_address, netmask, DHCPDHANDLERS[dhcp_handler], address_changed)

    def _disable_network(self, caller: str) -> None:
        self.confirm_authorization(caller, "org.blueman.network.setup")
        NetConf.clean_up()
