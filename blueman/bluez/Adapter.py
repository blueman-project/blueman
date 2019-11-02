# coding=utf-8
from gi.repository import GLib
from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase


class Adapter(Base):
    _interface_name = 'org.bluez.Adapter1'

    def __init__(self, obj_path):
        super().__init__(self._interface_name, obj_path=obj_path)

    def start_discovery(self):
        self._call('StartDiscovery')

    def stop_discovery(self):
        self._call('StopDiscovery')

    def remove_device(self, device):
        param = GLib.Variant('(o)', (device.get_object_path(),))
        self._call('RemoveDevice', param)

    def get_name(self):
        return self['Alias']

    def set_name(self, name):
        self.set('Alias', name)


class AnyAdapter(AnyBase):
    def __init__(self):
        super().__init__('org.bluez.Adapter1')
