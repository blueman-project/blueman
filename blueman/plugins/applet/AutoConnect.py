from gettext import gettext as _
from typing import TYPE_CHECKING, Union, Optional, Any

from gi.repository import GLib

from blueman.Sdp import ServiceUUID
from blueman.bluez.Device import Device
from blueman.config.AutoConnectConfig import AutoConnectConfig
from blueman.gui.Notification import Notification
from blueman.plugins.AppletPlugin import AppletPlugin

if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class AutoConnect(AppletPlugin):
    __depends__ = ["DBusService"]

    __icon__ = "bluetooth-symbolic"
    __author__ = "cschramm"
    __description__ = _("Tries to auto-connect to configurable services on start and every 60 seconds.")

    __gsettings__ = {
        "schema": "org.blueman.plugins.autoconnect",
        "path": None
    }
    __options__ = {
        "services": {"type": list, "default": "[]"}
    }

    def __init__(self, parent: "BluemanApplet"):
        super().__init__(parent)
        GLib.timeout_add(60000, self._run)

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self._run()

    def on_adapter_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Powered" and value:
            self._run()

    @staticmethod
    def __fix_settings(path: str, uuid: str) -> str:
        config = AutoConnectConfig()
        address = path.replace("_", ":")[-17:]

        data = set(config["services"])
        data.remove((path, uuid))
        data.add((address, uuid))
        config["services"] = data

        return address

    def _run(self) -> bool:
        for btaddress, uuid in self.get_option('services'):
            # We accidentally stored the dbus object path in 2.4
            if btaddress.startswith("/org/bluez"):
                btaddress = self.__fix_settings(btaddress, uuid)

            device = self.parent.Manager.find_device(btaddress)
            if device is None or device.get("Connected"):
                continue

            def reply(dev: Optional[Device] = device, service_name: str = ServiceUUID(uuid).name) -> None:
                assert isinstance(dev, Device)  # https://github.com/python/mypy/issues/2608
                Notification(_("Connected"), _("Automatically connected to %(service)s on %(device)s") %
                             {"service": service_name, "device": dev.display_name},
                             icon_name=dev["Icon"]).show()

            def err(_reason: Union[Exception, str]) -> None:
                pass

            self.parent.Plugins.DBusService.connect_service(device.get_object_path(), uuid, reply, err)

        return True
