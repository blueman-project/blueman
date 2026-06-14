from gettext import gettext as _
from typing import TYPE_CHECKING, Any
from blueman.bluemantyping import ObjectPath, BtAddress

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
        "services": {
            "type": list,
            "default": "[]"
        },
        "notification": {
            "type": bool,
            "default": True,
            "name": "Show notification",
            "desc": "Show a notification on successful autoconnect."
        },
        "interval": {
            "type": int,
            "default": 60,
            "range": (30, 1800),
            "name": "Connect interval",
            "desc": "Set the time in seconds an autoconnect is attempted."
        }
    }

    def __init__(self, parent: "BluemanApplet"):
        super().__init__(parent)
        self.__applet = parent
        self.__event_source: int | None = None

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self.start_timer()
        else:
            self.stop_timer()

    def option_changed(self, key: str, value: Any) -> None:
        if key == "interval":
            self.start_timer()

    def on_adapter_property_changed(self, path: ObjectPath, key: str, value: Any) -> None:
        if key == "Powered":
            if any(adapter["Powered"] for adapter in self.parent.Manager.get_adapters()):
                self.start_timer()
            else:
                self.stop_timer()

    def start_timer(self) -> None:
        if not self.__applet.manager_state:
            return

        self.stop_timer()

        powered = any(adapter["Powered"] for adapter in self.parent.Manager.get_adapters())
        if powered:
            self.__event_source = GLib.timeout_add_seconds(self.get_option("interval"), self._run)

    def stop_timer(self) -> None:
        if self.__event_source is not None:
            GLib.Source.remove(self.__event_source)
            self.__event_source = None

    @staticmethod
    def __fix_settings(path: ObjectPath, uuid: str) -> BtAddress:
        config = AutoConnectConfig()
        address = path.replace("_", ":")[-17:]

        data = set(config["services"])
        data.remove((path, uuid))
        data.add((address, uuid))
        config["services"] = data

        return BtAddress(address)

    def _run(self) -> bool:
        for btaddress, uuid in self.get_option('services'):
            # We accidentally stored the dbus object path in 2.4
            if btaddress.startswith("/org/bluez"):
                btaddress = self.__fix_settings(btaddress, uuid)

            device = self.parent.Manager.find_device(btaddress)
            if device is None or device.get("Connected"):
                continue

            def reply(dev: Device | None = device, service_name: str = ServiceUUID(uuid).name) -> None:
                if not self.get_option("notification"):
                    return

                assert isinstance(dev, Device)  # https://github.com/python/mypy/issues/2608
                Notification(_("Connected"), _("Automatically connected to %(service)s on %(device)s") %
                             {"service": service_name, "device": dev.display_name},
                             icon_name=dev["Icon"]).show()

            def err(_reason: Exception | str) -> None:
                pass

            self.parent.Plugins.DBusService.connect_service(device.get_object_path(), uuid, reply, err)

        return True
