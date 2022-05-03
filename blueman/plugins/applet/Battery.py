from gettext import gettext as _
from typing import Any

from blueman.bluez.Battery import Battery as BluezBattery
from blueman.bluez.Device import Device
from blueman.bluez.errors import BluezDBusException
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin


class Battery(AppletPlugin):
    __author__ = "cschramm"
    __icon__ = "battery"
    __description__ = _("Shows desktop notifications with battery percentage when devices get connected.")

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "ServicesResolved" and value:
            if self.applicable(path):
                text = "%d%%" % BluezBattery(obj_path=path)["Percentage"]
                Notification(Device(obj_path=path)["Alias"], text, icon_name="battery").show()

    @staticmethod
    def applicable(obj_path: str) -> bool:
        try:
            BluezBattery(obj_path=obj_path)["Percentage"]
            return True
        except BluezDBusException:
            return False
