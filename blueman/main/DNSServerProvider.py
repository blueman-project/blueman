import re
from ipaddress import IPv4Address
from typing import List, Generator

from gi.repository import GObject, Gio

from blueman.bluemantyping import GSignals


class DNSServerProvider(GObject.GObject):
    RESOLVER_PATH = "/etc/resolv.conf"

    __gsignals__: GSignals = {"changed": (GObject.SignalFlags.NO_HOOKS, None, ())}

    def __init__(self) -> None:
        super().__init__()
        self._subscribe_resolver()

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

    def _subscribe_resolver(self) -> None:
        self._monitor = Gio.File.new_for_path(self.RESOLVER_PATH).monitor_file(Gio.FileMonitorFlags.NONE)
        self._monitor.connect("changed", lambda *args: self.emit("changed"))
