from unittest import TestCase
from unittest.mock import patch, MagicMock

from gi.repository import GLib

from blueman.main.DBusProxies import (
    ProxyBase,
    AppletService,
    AppletDhcpClientService,
    AppletStatusIconService,
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

    # --- regression: the DhcpClient method lives on the right proxy ---

    def test_applet_service_has_no_dhcp_client(self):
        # NetworkService used to call AppletService().dchp_client(...) which
        # never existed on this interface. Lock that it stays absent here.
        self.assertFalse(hasattr(AppletService, "dchp_client"))

    def test_dhcp_client_proxy_exposes_method(self):
        self.assertTrue(hasattr(AppletDhcpClientService, "dchp_client"))

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

    # --- fuzz: every valid object path is forwarded verbatim, type "o" ---

    def test_dhcp_client_fuzz_valid_paths(self):
        # Object paths only allow [A-Za-z0-9_] segments separated by '/'.
        segments = ["org", "bluez", "hci0", "hci15", "dev_00_11_22_33_44_55",
                    "a", "A", "_", "x9", "Z_0"]
        paths = ["/"]  # the root path is valid
        for depth in range(1, len(segments) + 1):
            paths.append("/" + "/".join(segments[:depth]))
        # also a few address-shaped device paths
        for n in range(16):
            paths.append(f"/org/bluez/hci0/dev_{n:02d}_FF_FF_FF_FF_FF")

        for path in paths:
            with self.subTest(path=path):
                proxy = _make_proxy(AppletDhcpClientService)
                proxy.call_sync = MagicMock()
                proxy.dchp_client(path)
                args = proxy.call_sync.call_args.args
                self.assertEqual(args[0], "org.blueman.Applet.DhcpClient.DhcpClient")
                self.assertEqual(args[1].get_type_string(), "o")
                self.assertEqual(args[1].unpack(), path)

    def test_dhcp_client_fuzz_invalid_paths_raise(self):
        # Malformed object paths must be rejected by GLib before any D-Bus call.
        bad_paths = [
            "", "not-a-path", "relative/x", "/end/", "//double",
            "/has space", "/has-dash", "/has.dot", "/€uro", "/x/", " ",
        ]
        for path in bad_paths:
            with self.subTest(path=path):
                proxy = _make_proxy(AppletDhcpClientService)
                proxy.call_sync = MagicMock()
                with self.assertRaises((TypeError, ValueError, GLib.Error)):
                    proxy.dchp_client(path)
                proxy.call_sync.assert_not_called()

    # --- guard: AppletStatusIconService is a real, kept proxy ---

    def test_status_icon_service_is_proxy(self):
        # It carries no public methods on purpose: it exists to subscribe to
        # the org.blueman.Applet.StatusIcon interface signals in Tray.py.
        # Deleting it would silence IconName/Visibility/ToolTip updates, so it
        # must remain a ProxyBase subclass.
        self.assertTrue(issubclass(AppletStatusIconService, ProxyBase))
