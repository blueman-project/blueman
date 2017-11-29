# coding=utf-8
from gi.repository import GLib
from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase


class Adapter(Base):
    _interface_name = 'org.bluez.Adapter1'

    def __init__(self, obj_path=None):
        super().__init__(self._interface_name, obj_path=obj_path)

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
        super().__init__('org.bluez.Adapter1')
