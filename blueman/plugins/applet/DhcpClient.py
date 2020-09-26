from gettext import gettext as _
import logging
from typing import List, Any

from gi.repository import GLib

from blueman.bluez.Network import AnyNetwork, Network
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.DBusProxies import Mechanism


class DhcpClient(AppletPlugin):
    __description__ = _("Provides a basic dhcp client for Bluetooth PAN connections.")
    __icon__ = "network-workgroup"
    __author__ = "Walmis"

    _any_network = None

    def on_load(self) -> None:
        self._any_network = AnyNetwork()
        self._any_network.connect_signal('property-changed', self._on_network_prop_changed)

        self.quering: List[str] = []

        self._add_dbus_method("DhcpClient", ("s",), "", self.dhcp_acquire)

    def on_unload(self) -> None:
        del self._any_network

    def _on_network_prop_changed(self, _network: AnyNetwork, key: str, value: Any, object_path: str) -> None:
        if key == "Interface":
            if value != "":
                self.dhcp_acquire(object_path)

    def dhcp_acquire(self, object_path: str) -> None:
        device = Network(obj_path=object_path)["Interface"]

        if device not in self.quering:
            self.quering.append(device)
        else:
            return

        if device != "":
            def reply(_obj: Mechanism, result: str, _user_data: None) -> None:
                logging.info(result)
                Notification(_("Bluetooth Network"),
                             _("Interface %(0)s bound to IP address %(1)s") % {"0": device, "1": result},
                             icon_name="network-workgroup").show()

                self.quering.remove(device)

            def err(_obj: Mechanism, result: GLib.Error, _user_data: None) -> None:
                logging.warning(result)
                Notification(_("Bluetooth Network"), _("Failed to obtain an IP address on %s") % device,
                             icon_name="network-workgroup").show()

                self.quering.remove(device)

            Notification(_("Bluetooth Network"), _("Trying to obtain an IP address on %s\nPlease wait…" % device),
                         icon_name="network-workgroup").show()

            m = Mechanism()
            m.DhcpClient('(s)', object_path, result_handler=reply, error_handler=err, timeout=120 * 1000)
