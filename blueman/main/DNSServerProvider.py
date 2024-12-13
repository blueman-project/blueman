import re
import socket
from ipaddress import IPv4Address, ip_address
from collections.abc import Generator

from gi.repository import GObject, Gio, GLib

from blueman.bluemantyping import GSignals


class DNSServerProvider(GObject.GObject):
    RESOLVER_PATH = "/etc/resolv.conf"
    _RESOLVED_NAME = "org.freedesktop.resolve1"
    _RESOLVED_MANAGER_INTERFACE = "org.freedesktop.resolve1.Manager"

    __gsignals__: GSignals = {"changed": (GObject.SignalFlags.NO_HOOKS, None, ())}

    def __init__(self) -> None:
        super().__init__()
        self._subscribe_systemd_resolved()
        self._subscribe_resolver()

    @classmethod
    def get_servers(cls) -> list[IPv4Address]:
        return list(set(cls._get_servers_from_systemd_resolved()) or cls._get_servers_from_resolver())

    @classmethod
    def _get_servers_from_systemd_resolved(cls) -> Generator[IPv4Address, None, None]:
        bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)

        manager_proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SYSTEM,
            Gio.DBusProxyFlags.DO_NOT_AUTO_START,
            None,
            cls._RESOLVED_NAME,
            "/org/freedesktop/resolve1",
            cls._RESOLVED_MANAGER_INTERFACE,
        )

        try:
            data = manager_proxy.call_sync(
                "org.freedesktop.DBus.Properties.Get",
                GLib.Variant("(ss)", (cls._RESOLVED_MANAGER_INTERFACE, "DNS")),
                Gio.DBusCallFlags.NONE,
                -1,
                None
            ).unpack()[0]
        except GLib.Error:
            return

        for (interface, address_family, address) in data:
            if address_family != socket.AF_INET.value:
                continue

            if interface != 0:
                object_path = manager_proxy.call_sync(
                    "GetLink",
                    GLib.Variant("(i)", (interface,)),
                    Gio.DBusCallFlags.NONE,
                    -1,
                    None
                ).unpack()[0]

                if not bus.call_sync(
                    cls._RESOLVED_NAME,
                    object_path,
                    "org.freedesktop.DBus.Properties",
                    "Get",
                    GLib.Variant("(ss)", ("org.freedesktop.resolve1.Link", "DefaultRoute")),
                    None,
                    Gio.DBusCallFlags.NONE,
                    -1,
                    None
                ).unpack()[0]:
                    continue

            addr = ip_address('.'.join(str(p) for p in address))
            assert isinstance(addr, IPv4Address)
            yield addr

    @classmethod
    def _get_servers_from_resolver(cls) -> Generator[IPv4Address, None, None]:
        with open(cls.RESOLVER_PATH) as f:
            for line in f:
                match = re.search(r"^nameserver\s+((?:\d{1,3}\.){3}\d{1,3}$)", line)
                if match:
                    yield IPv4Address(match.group(1))

    def _subscribe_systemd_resolved(self) -> None:
        def on_signal(
            _connection: Gio.DBusConnection,
            _sender_name: str,
            _object_path: str,
            _interface_name: str,
            _signal_name: str,
            param: GLib.Variant,
        ) -> None:
            interface_name, changed_properties, invalidated_propeties = param.unpack()
            if interface_name == self._RESOLVED_MANAGER_INTERFACE and "DNS" in changed_properties:
                self.emit("changed")

        self._bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)

        self._bus.signal_subscribe(
            self._RESOLVED_NAME, "org.freedesktop.DBus.Properties", "PropertiesChanged",
            "/org/freedesktop/resolve1", None, Gio.DBusSignalFlags.NONE, on_signal)

    def _subscribe_resolver(self) -> None:
        self._monitor = Gio.File.new_for_path(self.RESOLVER_PATH).monitor_file(Gio.FileMonitorFlags.NONE)
        self._monitor.connect("changed", lambda *args: self.emit("changed"))
