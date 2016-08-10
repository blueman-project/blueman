# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject, Gio, GLib
from blueman.Functions import dprint
from blueman.bluez.Base import Base
from blueman.bluez.Device import Device
from blueman.bluez.AnyBase import AnyBase

class Adapter(Base):
    _interface_name = 'org.bluez.Adapter1'

    def _init(self, obj_path=None):
        super(Adapter, self)._init(self._interface_name, obj_path=obj_path)

        self._object_manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
            Gio.BusType.SYSTEM, Gio.DBusObjectManagerClientFlags.NONE,
            'org.bluez', '/', None, None, None)

    def find_device(self, address):
        for device in self.list_devices():
            if device['Address'] == address:
                return device

    def list_devices(self):
        paths = []
        for obj_proxy in self._object_manager.get_objects():
            proxy = obj_proxy.get_interface('org.bluez.Device1')

            if proxy:
                object_path = proxy.get_object_path()
                if object_path.startswith(self.get_object_path()):
                    paths.append(object_path)

        return [Device(path) for path in paths]

    def start_discovery(self):
        self._call('StartDiscovery')

    def stop_discovery(self):
        self._call('StopDiscovery')

    def remove_device(self, device):
        param = GLib.Variant('(o)', (device.get_object_path(),))
        self._call('RemoveDevice', param)

    # FIXME in BlueZ 5.31 getting and setting Alias appears to never fail
    def get_name(self):
        if 'Alias' in self:
            return self['Alias']
        else:
            return self['Name']

    def set_name(self, name):
        try:
            return self.set('Alias', name)
        except GLib.Error:
            return self.set('Name', name)

class AnyAdapter(AnyBase):
    def __init__(self):
        super(AnyAdapter, self).__init__('org.bluez.Adapter1')
