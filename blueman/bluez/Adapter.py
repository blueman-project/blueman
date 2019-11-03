# coding=utf-8
from gi.repository import GLib

from blueman.bluez.AnyBase import AnyBase
from blueman.bluez.Base import Base
from blueman.bluez.Device import Device


class Adapter(Base):
    _interface_name = 'org.bluez.Adapter1'

    def __init__(self, obj_path: str):
        super().__init__(interface_name=self._interface_name, obj_path=obj_path)

    def start_discovery(self) -> None:
        self._call('StartDiscovery')

    def stop_discovery(self) -> None:
        self._call('StopDiscovery')

    def remove_device(self, device: Device) -> None:
        param = GLib.Variant('(o)', (device.get_object_path(),))
        self._call('RemoveDevice', param)

    def get_name(self) -> str:
        name: str = self['Alias']
        return name

    def set_name(self, name: str) -> None:
        self.set('Alias', name)


class AnyAdapter(AnyBase):
    def __init__(self) -> None:
        super().__init__('org.bluez.Adapter1')
