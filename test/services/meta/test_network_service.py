from importlib import import_module
from unittest import TestCase
from unittest.mock import patch, MagicMock

from blueman.services.meta.NetworkService import NetworkService

# The package re-exports the NetworkService *class* under the name
# ``blueman.services.meta.NetworkService``, shadowing the submodule. Grab the
# actual module object so we can patch the proxy it imports.
network_service_module = import_module("blueman.services.meta.NetworkService")


def _make_service(object_path):
    # Bypass Service.__init__ (needs a real bluez Device); common_actions only
    # touches self.device.get_object_path().
    service = NetworkService.__new__(NetworkService)
    device = MagicMock()
    device.get_object_path.return_value = object_path
    # Service.device is a read-only property backed by a name-mangled attr.
    service._Service__device = device
    return service


class TestNetworkService(TestCase):
    def test_renew_dispatches_to_dhcp_client_proxy(self):
        path = "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"
        service = _make_service(path)
        action = next(iter(service.common_actions))

        with patch.object(network_service_module, "AppletDhcpClientService") as proxy_cls:
            action.callback()

        proxy_cls.assert_called_once_with()
        proxy_cls.return_value.dchp_client.assert_called_once_with(path)
