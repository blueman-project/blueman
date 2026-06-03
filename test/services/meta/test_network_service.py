from importlib import import_module
from unittest import TestCase
from unittest.mock import patch, MagicMock

from blueman.services.meta.NetworkService import NetworkService
from blueman.Service import Action

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
    def test_renew_action_present(self):
        service = _make_service("/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF")
        actions = service.common_actions
        self.assertEqual(len(actions), 1)
        action = next(iter(actions))
        self.assertIsInstance(action, Action)
        self.assertEqual(action.plugins, {"DhcpClient"})

    def test_renew_dispatches_to_dhcp_client_proxy(self):
        path = "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"
        service = _make_service(path)
        action = next(iter(service.common_actions))

        with patch.object(network_service_module, "AppletDhcpClientService") as proxy_cls:
            action.callback()

        proxy_cls.assert_called_once_with()
        proxy_cls.return_value.dchp_client.assert_called_once_with(path)

    def test_renew_does_not_use_bare_applet_service(self):
        # Regression: must route through AppletDhcpClientService, which is the
        # proxy that actually owns the dchp_client method.
        self.assertTrue(hasattr(network_service_module, "AppletDhcpClientService"))
        self.assertFalse(hasattr(network_service_module, "AppletService"))

    def test_renew_fuzz_passes_object_path_through(self):
        paths = ["/", "/org/bluez/hci0"]
        for n in range(32):
            paths.append(f"/org/bluez/hci{n}/dev_{n:02d}_11_22_33_44_55")

        for path in paths:
            with self.subTest(path=path):
                service = _make_service(path)
                action = next(iter(service.common_actions))
                with patch.object(network_service_module, "AppletDhcpClientService") as proxy_cls:
                    action.callback()
                proxy_cls.return_value.dchp_client.assert_called_once_with(path)
