import logging
from gettext import gettext as _
from typing import Any, Dict, Union
from blueman.bluemantyping import ObjectPath

from blueman.bluez.Device import Device
from blueman.gui.Notification import Notification, _NotificationBubble, _NotificationDialog
from blueman.main.BatteryWatcher import BatteryWatcher
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import GLib


class ConnectionNotifier(AppletPlugin):
    __author__ = "cschramm"
    __icon__ = "bluetooth-symbolic"
    __description__ = _("Shows desktop notifications when devices get connected or disconnected.")

    _notifications: Dict[ObjectPath, Union[_NotificationBubble, _NotificationDialog]] = {}

    def on_load(self) -> None:
        self._battery_watcher = BatteryWatcher(self._on_battery_update)
        self.connected = {}
        self.paring_state = {}
        self._add_dbus_method("SetParingState", ("s", "b"), "", self.set_paring_state)

    def on_unload(self) -> None:
        del self._battery_watcher
        del self.connected
        del self.paring_state

    def on_device_property_changed(self, path: ObjectPath, key: str, value: Any) -> None:
        if self.get_paring_state(path):
            self.set_paring_state(path, False)
            return
        
        if path not in self.connected:
            self.connected[path] = False
        
        if key == "Connected":
            device = Device(obj_path=path)
            if value:
                self.connected[path] = True
                self._notifications[path] = notification = Notification(
                    device.display_name,
                    _('Connected'),
                    icon_name=device["Icon"]
                )
                notification.show()
            elif self.connected[path]:
                self.connected[path] = False
                Notification(device.display_name, _('Disconnected'), icon_name=device["Icon"]).show()

    def _on_battery_update(self, path: ObjectPath, value: int) -> None:
        notification = self._notifications.pop(path, None)
        if notification:
            try:
                notification.set_message(f"{_('Connected')} {value}%")
                notification.set_notification_icon("battery")
            except GLib.Error:
                logging.error("Failed to update notification", exc_info=True)

    def get_paring_state(self, path: str) -> bool:
        if path not in self.paring_state:
            self.paring_state[path] = False
        return self.paring_state[path]
    
    def set_paring_state(self, path: str, new_paring_state: bool) -> None:
        self.paring_state[path] = new_paring_state