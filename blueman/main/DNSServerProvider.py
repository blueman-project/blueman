import re
from ipaddress import IPv4Address
from typing import List, Generator

from gi.repository import GObject


class DNSServerProvider(GObject.GObject):
    RESOLVER_PATH = "/etc/resolv.conf"

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_servers(cls) -> List[IPv4Address]:
        return list(cls._get_servers_from_resolver())

    @classmethod
    def _get_servers_from_resolver(cls) -> Generator[IPv4Address, None, None]:
        with open(cls.RESOLVER_PATH) as f:
            for line in f:
                match = re.search(r"^nameserver\s+((?:\d{1,3}\.){3}\d{1,3}$)", line)
                if match:
                    yield IPv4Address(match.group(1))
