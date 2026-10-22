from gettext import gettext as _

from blueman.bluez.Device import Device
from blueman.bluemantyping import BtAddress
from blueman.gui.manager.ManagerDeviceMenu import DeviceMenuItem, ManagerDeviceMenu, MenuItemsProvider
from blueman.plugins.ManagerPlugin import ManagerPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ConnectionNotifier(ManagerPlugin, MenuItemsProvider):
    __gsettings__ = {
        "schema": "org.blueman.general",
        "path": None
    }
    __options__ = {
        "connection-notification-disabled-devices": {
            "type": list,
            "default": []
        }
    }

    def _notifications_enabled(self, device: Device) -> bool:
        disabled_devices: list[BtAddress] = self.get_option("connection-notification-disabled-devices")
        return BtAddress(device["Address"]) not in disabled_devices

    def _set_notifications_enabled(self, device: Device, enabled: bool) -> None:
        address = BtAddress(device["Address"])
        disabled_devices: list[BtAddress] = self.get_option("connection-notification-disabled-devices")

        if enabled:
            disabled_devices = [dev for dev in disabled_devices if dev != address]
        elif address not in disabled_devices:
            disabled_devices.append(address)

        self.set_option("connection-notification-disabled-devices", disabled_devices)

    def on_request_menu_items(
        self,
        _manager_menu: ManagerDeviceMenu,
        device: Device,
        _powered: bool,
    ) -> list[DeviceMenuItem]:
        item = Gtk.CheckMenuItem.new_with_mnemonic(_("Show _notifications"))
        item.props.active = self._notifications_enabled(device)
        item.props.tooltip_text = _("Show notifications when this device connects or disconnects")
        item.connect("toggled", lambda x: self._set_notifications_enabled(device, x.props.active))
        item.show()
        return [DeviceMenuItem(item, DeviceMenuItem.Group.ACTIONS, 600)]
