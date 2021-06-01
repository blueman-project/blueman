from gettext import gettext as _
from typing import Callable, Union, TYPE_CHECKING

from _blueman import RFCOMMError
from gi.repository import GLib

from blueman.Service import Service
from blueman.bluez.errors import BluezDBusException
if TYPE_CHECKING:
    from blueman.main.NetworkManager import NMConnectionError
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Device import Device
from blueman.services.Functions import get_service

import logging

from blueman.services.meta import SerialService, NetworkService


class RFCOMMConnectedListener:
    def on_rfcomm_connected(self, service: SerialService, port: str) -> None:
        ...

    def on_rfcomm_disconnect(self, port: int) -> None:
        ...


class RFCOMMConnectHandler:
    def rfcomm_connect_handler(self, service: SerialService, reply: Callable[[str], None],
                               err: Callable[[Union[RFCOMMError, GLib.Error]], None]) -> bool:
        ...


class ServiceConnectHandler:
    def service_connect_handler(self, service: Service, ok: Callable[[], None],
                                err: Callable[[Union["NMConnectionError", GLib.Error]], None]) -> bool:
        ...

    def service_disconnect_handler(self, service: Service, ok: Callable[[], None],
                                   err: Callable[[Union["NMConnectionError", GLib.Error]], None]) -> bool:
        ...


class DBusService(AppletPlugin):
    __depends__ = ["StatusIcon"]
    __unloadable__ = False
    __description__ = _("Provides DBus API for other Blueman components")
    __author__ = "Walmis"

    def on_load(self) -> None:
        self._add_dbus_method("QueryPlugins", (), "as", self.parent.Plugins.get_loaded)
        self._add_dbus_method("QueryAvailablePlugins", (), "as", lambda: list(self.parent.Plugins.get_classes()))
        self._add_dbus_method("SetPluginConfig", ("s", "b"), "", self.parent.Plugins.set_config)
        self._add_dbus_method("ConnectService", ("o", "s"), "", self.connect_service, is_async=True)
        self._add_dbus_method("DisconnectService", ("o", "s", "d"), "", self._disconnect_service, is_async=True)
        self._add_dbus_method("OpenPluginDialog", (), "", self._open_plugin_dialog)

    def connect_service(self, object_path: str, uuid: str, ok: Callable[[], None],
                        err: Callable[[Union[BluezDBusException, "NMConnectionError",
                                             RFCOMMError, GLib.Error, str]], None]) -> None:
        try:
            self.parent.Plugins.RecentConns
        except KeyError:
            logging.warning("RecentConns plugin is unavailable")
        else:
            self.parent.Plugins.RecentConns.notify(object_path, uuid)

        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(obj_path=object_path)
            device.connect(reply_handler=ok, error_handler=err)
        else:
            service = get_service(Device(obj_path=object_path), uuid)
            assert service is not None

            if any(plugin.service_connect_handler(service, ok, err)
                   for plugin in self.parent.Plugins.get_loaded_plugins(ServiceConnectHandler)):
                pass
            elif isinstance(service, SerialService):
                def reply(rfcomm: str) -> None:
                    assert isinstance(service, SerialService)  # https://github.com/python/mypy/issues/2608
                    for plugin in self.parent.Plugins.get_loaded_plugins(RFCOMMConnectedListener):
                        plugin.on_rfcomm_connected(service, rfcomm)
                    ok()

                if not any(plugin.rfcomm_connect_handler(service, reply, err)
                           for plugin in self.parent.Plugins.get_loaded_plugins(RFCOMMConnectHandler)):
                    service.connect(reply_handler=lambda port: ok(), error_handler=err)
            elif isinstance(service, NetworkService):
                service.connect(reply_handler=lambda interface: ok(), error_handler=err)
            else:
                logging.info("No handler registered")
                err("Service not supported\nPossibly the plugin that handles this service is not loaded")

    def _disconnect_service(self, object_path: str, uuid: str, port: int, ok: Callable[[], None],
                            err: Callable[[Union[BluezDBusException, "NMConnectionError",
                                                 GLib.Error, str]], None]) -> None:
        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(obj_path=object_path)
            device.disconnect(reply_handler=ok, error_handler=err)
        else:
            service = get_service(Device(obj_path=object_path), uuid)
            assert service is not None

            if any(plugin.service_disconnect_handler(service, ok, err)
                   for plugin in self.parent.Plugins.get_loaded_plugins(ServiceConnectHandler)):
                pass
            elif isinstance(service, SerialService):
                service.disconnect(port, reply_handler=ok, error_handler=err)

                for plugin in self.parent.Plugins.get_loaded_plugins(RFCOMMConnectedListener):
                    plugin.on_rfcomm_disconnect(port)

                logging.info("Disconnecting rfcomm device")
            elif isinstance(service, NetworkService):
                service.disconnect(reply_handler=ok, error_handler=err)

    def _open_plugin_dialog(self) -> None:
        self.parent.Plugins.StandardItems.on_plugins()
