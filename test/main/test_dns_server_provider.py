from ipaddress import IPv4Address
from typing import Callable
from unittest.mock import patch, Mock

from dbusmock import DBusTestCase
from gi.repository import GLib, Gio

from blueman.main.DNSServerProvider import DNSServerProvider
from test.testhelpers.DBusMock import DBusMock


@patch("blueman.main.DNSServerProvider.DNSServerProvider.RESOLVER_PATH", "/tmp/resolv.conf")
@patch(
    "blueman.main.DNSServerProvider.Gio.bus_get_sync",
    lambda bus_type: Gio.DBusConnection.new_for_address_sync(
        Gio.dbus_address_get_for_bus_sync(bus_type),
        Gio.DBusConnectionFlags.MESSAGE_BUS_CONNECTION | Gio.DBusConnectionFlags.AUTHENTICATION_CLIENT,
    )
)
class TestDNSServerProvider(DBusTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.start_system_bus()

    def test_resolver(self):
        with open("/tmp/resolv.conf", "w") as f:
            f.write("""# Test configuration
search mynet
nameserver 192.0.2.1
nameserver 2001:db8::1
nameserver 198.51.100.1""")

        self.assertListEqual(
            DNSServerProvider.get_servers(),
            [IPv4Address("192.0.2.1"), IPv4Address("198.51.100.1")]
        )

    def test_systemd_resolved(self):
        with DBusMock("org.freedesktop.resolve1", "/org/freedesktop/resolve1", Gio.BusType.SYSTEM) as mock:
            mock.add_property("org.freedesktop.resolve1.Manager", "DNS",
                              GLib.Variant("a(iiay)", [
                                  (0, 2, [203, 0, 113, 1]),
                                  (0, 10, [0x20, 0x01, 0x0d, 0xb8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x01]),
                                  (3, 2, [198, 51, 100, 32]),
                                  (3, 10, [0x20, 0x01, 0x0d, 0xb8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x02]),
                                  (5, 2, [198, 51, 100, 64]),
                                  (5, 10, [0x20, 0x01, 0x0d, 0xb8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x03]),
                              ]))
            mock.add_method("org.freedesktop.resolve1.Manager", "GetLink", "i", "s",
                            "ret = f'/org/freedesktop/resolve1/link/_3{args[0]}'")
            mock.add_object("/org/freedesktop/resolve1/link/_33")\
                .add_property("org.freedesktop.resolve1.Link", "DefaultRoute", GLib.Variant("b", True))
            mock.add_object("/org/freedesktop/resolve1/link/_35")\
                .add_property("org.freedesktop.resolve1.Link", "DefaultRoute", GLib.Variant("b", False))

            self.assertListEqual(
                sorted(DNSServerProvider.get_servers()),
                [IPv4Address("198.51.100.32"), IPv4Address("203.0.113.1")]
            )

    def test_resolver_changed(self):
        self._test_changed(lambda: open("/tmp/resolv.conf", "w").close())

    def test_resolved_changed(self):
        def trigger():
            with DBusMock("org.freedesktop.resolve1", "/org/freedesktop/resolve1", Gio.BusType.SYSTEM) as dbus_mock:
                dbus_mock.add_property("org.freedesktop.resolve1.Manager", "DNS", GLib.Variant("a(iiay)", []))
                dbus_mock.set_property("org.freedesktop.resolve1.Manager", "DNS", GLib.Variant("a(iiay)", []))

        self._test_changed(trigger)

    @staticmethod
    def _test_changed(action: Callable[[], None]) -> None:
        mock = Mock()
        provider = DNSServerProvider()
        provider.connect("changed", mock)

        action()

        context = GLib.MainContext.default()
        while context.pending():
            context.iteration()
        mock.assert_called_with(provider)
