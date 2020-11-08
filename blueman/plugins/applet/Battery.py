from gettext import gettext as _
from typing import Any

from blueman.Sdp import ServiceUUID, BATTERY_SERVICE_SVCLASS_ID
from blueman.bluez.Battery import Battery as BluezBattery
from blueman.bluez.Device import Device
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin


class Battery(AppletPlugin):
    __author__ = "cschramm"
    __icon__ = "battery"
    __description__ = _("Shows desktop notifications with battery percentage when devices get connected.")

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "ServicesResolved" and value:
            device = Device(obj_path=path)
            if self.applicable(device):
                text = "%d%%" % BluezBattery(obj_path=path)["Percentage"]
                Notification(device["Alias"], text, icon_name="battery").show()

    @staticmethod
    def applicable(device: Device) -> bool:
        return any(ServiceUUID(uuid).short_uuid == BATTERY_SERVICE_SVCLASS_ID for uuid in device["UUIDs"])
