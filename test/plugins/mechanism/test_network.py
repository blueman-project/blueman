from unittest import TestCase
from unittest.mock import patch, Mock

from blueman.plugins.mechanism import Network as network_module
from blueman.plugins.mechanism.Network import Network, DHCPDHANDLERS


def _make_network():
    # MechanismPlugin.__init__ takes timer/confirm_authorization off the parent
    # and calls on_load(), which only registers methods on the (mock) parent.
    return Network(Mock())


class TestEnableNetworkHandlerValidation(TestCase):
    def test_known_handlers_dispatch(self):
        for name, cls in DHCPDHANDLERS.items():
            with self.subTest(handler=name):
                net = _make_network()
                with patch.object(network_module.NetConf, "apply_settings") as apply_mock:
                    net._enable_network("203.0.113.1", "255.255.255.0", name, False, ":1.1")
                apply_mock.assert_called_once_with("203.0.113.1", "255.255.255.0", cls, False)

    def test_unknown_handler_raises_before_apply(self):
        net = _make_network()
        with patch.object(network_module.NetConf, "apply_settings") as apply_mock:
            with self.assertRaises(ValueError):
                net._enable_network("203.0.113.1", "255.255.255.0", "bogus", False, ":1.1")
        apply_mock.assert_not_called()

    def test_fuzz_unknown_keys_never_keyerror(self):
        bad_keys = [
            "", "dnsmasqhandler", "DnsMasqHandler ", " DnsMasqHandler",
            "__class__", "../etc", "DnsMasq", "None", "0", "🚀",
            "DnsMasqHandler\n", "DHCPDHANDLERS",
        ]
        for key in bad_keys:
            with self.subTest(key=key):
                net = _make_network()
                with patch.object(network_module.NetConf, "apply_settings") as apply_mock:
                    with self.assertRaises(ValueError):
                        net._enable_network("203.0.113.1", "255.255.255.0", key, False, ":1.1")
                    apply_mock.assert_not_called()
