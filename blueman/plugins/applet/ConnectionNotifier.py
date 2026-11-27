import logging
from gettext import gettext as _
from typing import Any
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

    _notifications: dict[ObjectPath, _NotificationBubble | _NotificationDialog] = {}
    _pending: dict[ObjectPath, int] = {}

    def on_load(self) -> None:
        self._battery_watcher = BatteryWatcher(self._on_battery_update)
        self._pending = {}

    def on_unload(self) -> None:
        for timer_id in self._pending.values():
            GLib.source_remove(timer_id)
        self._pending.clear()
        del self._battery_watcher

    def on_device_property_changed(self, path: ObjectPath, key: str, value: Any) -> None:
        if key == "Connected":
            pending = self._pending.pop(path, None)
            if pending is not None:
                GLib.source_remove(pending)
                return

            self._pending[path] = GLib.timeout_add_seconds(2, self._notify_connection, path, bool(value))

    def _notify_connection(self, path: ObjectPath, connected: bool) -> bool:
        self._pending.pop(path, None)
        device = Device(obj_path=path)
        if connected:
            self._notifications[path] = notification = Notification(
                device.display_name,
                _('Connected'),
                icon_name=device["Icon"],
                transient=True,
            )
            notification.show()
        else:
            Notification(
                device.display_name,
                _('Disconnected'),
                icon_name=device["Icon"],
                transient=True,
            ).show()
        return False

    def _on_battery_update(self, path: ObjectPath, value: int) -> None:
        notification = self._notifications.pop(path, None)
        if notification:
            try:
                notification.set_message(f"{_('Connected')} {value}%")
                notification.set_notification_icon("battery")
            except GLib.Error:
                logging.error("Failed to update notification", exc_info=True)
