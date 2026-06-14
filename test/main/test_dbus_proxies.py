from unittest import TestCase
from unittest.mock import patch, MagicMock

from blueman.main.DBusProxies import (
    ProxyBase,
    AppletDhcpClientService,
)
from blueman.gobject import SingletonGObjectMeta


def _make_proxy(cls):
    """Instantiate a ProxyBase subclass without touching a real D-Bus bus.

    ProxyBase.__init__ would call Gio.DBusProxy.init() which needs a live bus.
    We bypass it and reset the singleton cache so other tests are unaffected.
    """
    with patch.object(ProxyBase, "__init__", return_value=None):
        cls._instance = None
        instance = cls()
    cls._instance = None
    return instance


class TestDBusProxies(TestCase):
    def test_metaclass(self):
        self.assertIsInstance(ProxyBase, SingletonGObjectMeta)

    def test_dhcp_client_dispatches_to_dbus(self):
        proxy = _make_proxy(AppletDhcpClientService)
        proxy.call_sync = MagicMock()

        path = "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"
        proxy.dchp_client(path)

        proxy.call_sync.assert_called_once()
        args = proxy.call_sync.call_args.args
        self.assertEqual(args[0], "org.blueman.Applet.DhcpClient.DhcpClient")
        self.assertEqual(args[1].get_type_string(), "o")
        self.assertEqual(args[1].unpack(), path)
