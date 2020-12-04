from typing import List

from gi.repository import GObject
from gi.repository import GLib
import socket
import subprocess
import logging
from blueman.Functions import have, get_local_interfaces
from blueman.bluemantyping import GSignals


class DhcpClient(GObject.GObject):
    __gsignals__: GSignals = {
        # arg: interface name eg. ppp0
        'connected': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'error-occurred': (GObject.SignalFlags.NO_HOOKS, None, (int,)),
    }

    COMMANDS = [
        ["dhclient", "-e", "IF_METRIC=100", "-1"],
        ["dhcpcd", "-m", "100"],
        ["udhcpc", "-t", "20", "-x", "hostname", socket.gethostname(), "-n", "-i"]
    ]

    quering: List[str] = []

    def __init__(self, interface: str, timeout: int = 30) -> None:
        """The interface name has to be trusted / sanitized!"""
        super().__init__()

        self._interface = interface
        self._timeout = timeout

        self._command = None
        for command in self.COMMANDS:
            path = have(command[0])
            if path:
                self._command = [path] + command[1:] + [self._interface]
                break

    def run(self) -> None:
        if not self._command:
            raise Exception("No DHCP client found, please install dhclient, dhcpcd, or udhcpc")

        if self._interface in DhcpClient.quering:
            raise Exception("DHCP already running on this interface")
        else:
            DhcpClient.quering.append(self._interface)

        self._client = subprocess.Popen(self._command)
        GLib.timeout_add(1000, self._check_client)
        GLib.timeout_add(self._timeout * 1000, self._on_timeout)

    def _on_timeout(self) -> bool:
        if not self._client.poll():
            logging.warning("Timeout reached, terminating DHCP client")
            self._client.terminate()
        return False

    def _check_client(self) -> bool:
        netifs = get_local_interfaces()
        status = self._client.poll()
        if status == 0:
            def complete() -> bool:
                ip = netifs[self._interface][0]
                logging.info(f"bound to {ip}")
                self.emit("connected", ip)
                return False

            GLib.timeout_add(1000, complete)
            DhcpClient.quering.remove(self._interface)
            return False
        elif status:
            logging.error(f"dhcp client failed with status code {status}")
            self.emit("error-occurred", status)
            DhcpClient.quering.remove(self._interface)
            return False
        else:
            return True
