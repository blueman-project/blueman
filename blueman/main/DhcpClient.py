# coding=utf-8
from gi.repository import GObject
from gi.repository import GLib
import socket
import subprocess
import logging
from blueman.Functions import have
from _blueman import get_net_address


class DhcpClient(GObject.GObject):
    __gsignals__ = {
        # arg: interface name eg. ppp0
        'connected': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'error-occurred': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    COMMANDS = [
        ["dhclient", "-e", "IF_METRIC=100", "-1"],
        ["dhcpcd", "-m", "100"],
        ["udhcpc", "-t", "20", "-x", "hostname", socket.gethostname(), "-n", "-i"]
    ]

    quering = []

    def __init__(self, interface, timeout=30):
        super().__init__()

        self._interface = interface
        self._timeout = timeout

        self._command = None
        for command in self.COMMANDS:
            path = have(command[0])
            if path:
                self._command = [path] + command[1:] + [self._interface]
                break
        self._client = None

    def run(self):
        if not self._command:
            raise Exception("No DHCP client found, please install dhclient, dhcpcd, or udhcpc")

        if self._interface in DhcpClient.quering:
            raise Exception("DHCP already running on this interface")
        else:
            DhcpClient.quering.append(self._interface)

        self._client = subprocess.Popen(self._command)
        GLib.timeout_add(1000, self._check_client)
        GLib.timeout_add(self._timeout * 1000, self._on_timeout)

    def _on_timeout(self):
        if not self._client.poll():
            logging.warning("Timeout reached, terminating DHCP client")
            self._client.terminate()

    def _check_client(self):
        status = self._client.poll()
        if status == 0:
            def complete():
                ip = get_net_address(self._interface)
                logging.info("bound to %s" % ip)
                self.emit("connected", ip)

            GLib.timeout_add(1000, complete)
            DhcpClient.quering.remove(self._interface)
            return False
        elif status:
            logging.error("dhcp client failed with status code %s" % status)
            self.emit("error-occurred", status)
            DhcpClient.quering.remove(self._interface)
            return False
        else:
            return True
