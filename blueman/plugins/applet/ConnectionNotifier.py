import logging
from gettext import gettext as _
from typing import Any, Optional, Dict, Union

from blueman.bluez.Device import Device
from blueman.bluez.Battery import Battery
from blueman.bluez.Manager import Manager
from blueman.bluez.errors import BluezDBusException
from blueman.gui.Notification import Notification, _NotificationBubble, _NotificationDialog
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import GLib


class ConnectionNotifier(AppletPlugin):
    __author__ = "cschramm"
    __icon__ = "bluetooth-symbolic"
    __description__ = _("Shows desktop notifications when devices get connected or disconnected.")

    _sig = None
    _notifications: Dict[str, Union[_NotificationBubble, _NotificationDialog]] = {}

    def on_load(self) -> None:
        self._manager = Manager()
        self._sig = self._manager.connect_signal("battery-created", self._on_battery_created)

    def on_unload(self) -> None:
        if self._sig is not None:
            self._manager.disconnect_signal(self._sig)

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        device = Device(obj_path=path)
        battery = Battery(obj_path=path)

        if key == "Connected":
            if value:
                try:
                    perc = battery['Percentage']
                    icon_name = "battery"
                except BluezDBusException:
                    logging.debug("Failed to get battery level")
                    perc = None
                    icon_name = device["Icon"]

                self._notifications[path] = notification = Notification(
                    device["Alias"],
                    self._get_message(perc),
                    icon_name=icon_name
                )
                notification.show()

                sig = battery.connect_signal("property-changed", self._on_battery_property_changed)

                def disconnect_signal() -> bool:
                    battery.disconnect_signal(sig)
                    return False
                GLib.timeout_add_seconds(5, disconnect_signal)
            else:
                Notification(device["Alias"], _('Disconnected'), icon_name=device["Icon"]).show()

    def _get_message(self, battery_percentage: Optional[str]) -> str:
        if battery_percentage is None:
            return _('Connected')
        else:
            return f"{_('Connected')} {battery_percentage}%"

    def _on_battery_created(self, _manager: Manager, obj_path: str) -> None:
        battery = Battery(obj_path=obj_path)
        self._on_battery_property_changed(battery, "Percentage", battery["Percentage"], obj_path)

    def _on_battery_property_changed(self, _battery: Battery, key: str, value: Any, path: str) -> None:
        if key == "Percentage":
            notification = self._notifications[path]
            if notification:
                notification.set_message(self._get_message(value))
