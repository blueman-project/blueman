from ipaddress import IPv4Address
from unittest import TestCase
from unittest.mock import patch

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
