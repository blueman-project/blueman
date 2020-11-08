from gettext import gettext as _
from typing import Any

from blueman.bluez.Device import Device
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.applet.Battery import Battery


class ConnectionNotifier(AppletPlugin):
    __author__ = "cschramm"
    __icon__ = "blueman-active"
    __description__ = _("Shows desktop notifications when devices get connected or disconnected.")

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected":
            device = Device(obj_path=path)
            if value and "Battery" in self.parent.Plugins.get_loaded() and Battery.applicable(device):
                return

            Notification(device["Alias"], _("Connected") if value else _("Disconnected"),
                         icon_name=device["Icon"]).show()
