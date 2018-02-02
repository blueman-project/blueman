# coding=utf-8
from gi.repository import GObject, Gio
from gi.types import GObjectMeta
import logging

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.bluez.errors import DBusNoSuchAdapterError


class ManagerMeta(GObjectMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)

        return cls._instance


class Manager(GObject.GObject, metaclass=ManagerMeta):
    __gsignals__ = {
        'adapter-added': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'adapter-removed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'device-created': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'device-removed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez'

    def __init__(self):
        super().__init__()
        self._object_manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
            Gio.BusType.SYSTEM, Gio.DBusObjectManagerClientFlags.DO_NOT_AUTO_START,
            self.__bus_name, '/', None, None, None)

        self._object_manager.connect("object-added", self._on_object_added)
        self._object_manager.connect("object-removed", self._on_object_removed)

    def _on_object_added(self, object_manager, dbus_object):
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

    def _on_object_removed(self, object_manager, dbus_object):
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

    def get_adapters(self):
        paths = []
        for obj_proxy in self._object_manager.get_objects():
            proxy = obj_proxy.get_interface('org.bluez.Adapter1')

            if proxy:
                paths.append(proxy.get_object_path())

        return [Adapter(path) for path in paths]

    def get_adapter(self, pattern=None):
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

    def get_devices(self, adapter_path='/'):
        paths = []
        for obj_proxy in self._object_manager.get_objects():
            proxy = obj_proxy.get_interface('org.bluez.Device1')

            if proxy:
                object_path = proxy.get_object_path()
                if object_path.startswith(adapter_path):
                    paths.append(object_path)

        return [Device(path) for path in paths]

    def find_device(self, address, adapter_path='/'):
        for device in self.get_devices(adapter_path):
            if device['Address'] == address:
                return device

    @classmethod
    def watch_name_owner(cls, appeared_handler, vanished_handler):
        Gio.bus_watch_name(Gio.BusType.SYSTEM, cls.__bus_name, Gio.BusNameWatcherFlags.AUTO_START,
                           appeared_handler, vanished_handler)
