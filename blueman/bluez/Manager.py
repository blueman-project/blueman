# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from gi.repository import GObject, Gio
from blueman.Functions import dprint

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device


class Manager(Gio.DBusObjectManagerClient):
    __gsignals__ = {
        str('adapter-added'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('adapter-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('device-created'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('device-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez'
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Manager, cls).__new__(cls)
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    def _init(self):
        super(Manager, self).__init__(
            bus_type = Gio.BusType.SYSTEM,
            flags = Gio.DBusObjectManagerClientFlags.NONE,
            name = self.__bus_name,
            object_path = '/')
        self.init()

    def do_object_added(self, dbus_object):
        device_proxy = dbus_object.get_interface('org.bluez.Device1')
        adapter_proxy = dbus_object.get_interface('org.bluez.Adapter1')

        if adapter_proxy:
            object_path = adapter_proxy.get_object_path()
            dprint(object_path)
            self.emit('adapter-added', object_path)
        elif device_proxy:
            object_path = device_proxy.get_object_path()
            dprint(object_path)
            self.emit('device-created', object_path)

    def do_object_removed(self, dbus_object):
        device_proxy = dbus_object.get_interface('org.bluez.Device1')
        adapter_proxy = dbus_object.get_interface('org.bluez.Adapter1')

        if adapter_proxy:
            object_path = adapter_proxy.get_object_path()
            dprint(object_path)
            self.emit('adapter-removed', object_path)
        elif device_proxy:
            object_path = device_proxy.get_object_path()
            dprint(object_path)
            self.emit('device-removed', object_path)

    def get_adapters(self):
        paths = []
        for obj_proxy in self.get_objects():
            proxy = obj_proxy.get_interface('org.bluez.Adapter1')

            if proxy: paths.append(proxy.get_object_path())

        return [Adapter(path) for path in paths]

    def get_adapter(self, pattern=None):
        adapters = self.get_adapters()
        if pattern is None:
            if len(adapters):
                return adapters[0]
        else:
            for adapter in adapters:
                path = adapter.get_object_path()
                if path.endswith(pattern) or adapter.get_properties()['Address'] == pattern:
                    return adapter

    def get_devices(self, adapter_path='/'):
        paths = []
        for obj_proxy in self.get_objects():
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
