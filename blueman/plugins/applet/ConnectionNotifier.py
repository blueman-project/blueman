import logging
from gettext import gettext as _
from typing import Any

from blueman.bluez.Device import Device
from blueman.bluez.Battery import Battery
from blueman.bluez.errors import BluezDBusException
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import GLib


class ConnectionNotifier(AppletPlugin):
    __author__ = "cschramm"
    __icon__ = "bluetooth-symbolic"
    __description__ = _("Shows desktop notifications when devices get connected or disconnected.")

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        def show_notification() -> bool:
            try:
                perc = f"{battery['Percentage']}%"
                icon_name = "battery"
            except BluezDBusException:
                perc = None
                icon_name = device["Icon"]
                logging.debug("Failed to get battery level")

            txt = f"{_('Connected')} {perc if perc is not None else ''}"
            Notification(device["Alias"], txt, icon_name=icon_name).show()
            return False

        device = Device(obj_path=path)
        battery = Battery(obj_path=path)

        if key == "Connected":
            if value:
                # FIXME delay is needed for battery info. Most notably xbox one pads #1696
                GLib.timeout_add_seconds(5, show_notification)
            else:
                Notification(device["Alias"], _('Disconnected'), icon_name=device["Icon"]).show()
