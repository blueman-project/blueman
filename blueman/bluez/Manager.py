import logging
from typing import List, Optional, Callable

from gi.repository import GObject, Gio

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.bluez.errors import DBusNoSuchAdapterError
from blueman.gobject import SingletonGObjectMeta
from blueman.typing import GSignals


class Manager(GObject.GObject, metaclass=SingletonGObjectMeta):
    __gsignals__: GSignals = {
        'adapter-added': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'adapter-removed': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'device-created': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'device-removed': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez'

    def __init__(self) -> None:
        super().__init__()
        self._object_manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
            Gio.BusType.SYSTEM, Gio.DBusObjectManagerClientFlags.DO_NOT_AUTO_START,
            self.__bus_name, '/', None, None, None)

        self._object_manager.connect("object-added", self._on_object_added)
        self._object_manager.connect("object-removed", self._on_object_removed)

    def _on_object_added(self, _object_manager: Gio.DBusObjectManager, dbus_object: Gio.DBusObject) -> None:
        device_proxy = dbus_object.get_interface('org.bluez.Device1')
        adapter_proxy = dbus_object.get_interface('org.bluez.Adapter1')

        if adapter_proxy:
            object_path = adapter_proxy.get_object_path()
            logging.debug(object_path)
            self.emit('adapter-added', object_path)
        elif device_proxy:
            object_path = device_proxy.get_object_path()
            logging.debug(object_path)
            self.emit('device-created', object_path)

    def _on_object_removed(self, _object_manager: Gio.DBusObjectManager, dbus_object: Gio.DBusObject) -> None:
        device_proxy = dbus_object.get_interface('org.bluez.Device1')
        adapter_proxy = dbus_object.get_interface('org.bluez.Adapter1')

        if adapter_proxy:
            object_path = adapter_proxy.get_object_path()
            logging.debug(object_path)
            self.emit('adapter-removed', object_path)
        elif device_proxy:
            object_path = device_proxy.get_object_path()
            logging.debug(object_path)
            self.emit('device-removed', object_path)

    def get_adapters(self) -> List[Adapter]:
        paths = []
        for obj_proxy in self._object_manager.get_objects():
            proxy = obj_proxy.get_interface('org.bluez.Adapter1')

            if proxy:
                paths.append(proxy.get_object_path())

        return [Adapter(obj_path=path) for path in paths]

    def get_adapter(self, pattern: Optional[str] = None) -> Adapter:
        adapters = self.get_adapters()
        if pattern is None:
            if len(adapters):
                return adapters[0]
            else:
                raise DBusNoSuchAdapterError("No adapter(s) found")
        else:
            for adapter in adapters:
                path = adapter.get_object_path()
                if path.endswith(pattern) or adapter['Address'] == pattern:
                    return adapter
            raise DBusNoSuchAdapterError("No adapters found with pattern: %s" % pattern)

    def get_devices(self, adapter_path: str = "/") -> List[Device]:
        paths = []
        for obj_proxy in self._object_manager.get_objects():
            proxy = obj_proxy.get_interface('org.bluez.Device1')

            if proxy:
                object_path = proxy.get_object_path()
                if object_path.startswith(adapter_path):
                    paths.append(object_path)

        return [Device(obj_path=path) for path in paths]

    def find_device(self, address: str, adapter_path: str = "/") -> Optional[Device]:
        for device in self.get_devices(adapter_path):
            if device['Address'] == address:
                return device
        return None

    @classmethod
    def watch_name_owner(
        cls,
        appeared_handler: Callable[[Gio.DBusConnection, str, str], None],
        vanished_handler: Callable[[Gio.DBusConnection, str], None],
    ) -> None:
        Gio.bus_watch_name(Gio.BusType.SYSTEM, cls.__bus_name, Gio.BusNameWatcherFlags.AUTO_START,
                           appeared_handler, vanished_handler)
