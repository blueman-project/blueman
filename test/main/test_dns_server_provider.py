from ipaddress import IPv4Address
from typing import Callable
from unittest import TestCase
from unittest.mock import patch, Mock

from gi.repository import GLib

from blueman.main.DNSServerProvider import DNSServerProvider


@patch("blueman.main.DNSServerProvider.DNSServerProvider.RESOLVER_PATH", "/tmp/resolv.conf")
class TestDNSServerProvider(TestCase):
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

    def test_resolver_changed(self):
        self._test_changed(lambda: open("/tmp/resolv.conf", "w").close())

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
