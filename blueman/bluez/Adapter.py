from collections.abc import Callable
from typing import cast
from blueman.bluemantyping import ObjectPath, BtAddress

from gi.repository import GLib

from blueman.bluez.AnyBase import AnyBase
from blueman.bluez.Base import Base
from blueman.bluez.Device import Device
from blueman.bluez.errors import BluezDBusException


class Adapter(Base):
    _interface_name = 'org.bluez.Adapter1'

    def __init__(self, obj_path: ObjectPath):
        super().__init__(obj_path=obj_path)

    def start_discovery(self, error_handler: Callable[[BluezDBusException], None] | None = None) -> None:
        self._call('StartDiscovery', error_handler=error_handler)

    def stop_discovery(self) -> None:
        self._call('StopDiscovery')

    def remove_device(self, device: Device) -> None:
        param = GLib.Variant('(o)', (device.get_object_path(),))
        self._call('RemoveDevice', param)

    @property
    def address(self) -> BtAddress:
        return cast(BtAddress, self.get("Address"))

    @property
    def alias(self) -> str:
        return cast(str, self.get("Alias"))

    @alias.setter
    def alias(self, alias: str) -> None:
        self.set("Alias", alias)

    @property
    def discoverable(self) -> bool:
        return cast(bool, self.get("Discoverable"))

    @discoverable.setter
    def discoverable(self, v: bool) -> None:
        self.set("Discoverable", v)

    @property
    def discoverable_timeout(self) -> int:
        return cast(int, self.get("DiscoverableTimeout"))

    @discoverable_timeout.setter
    def discoverable_timeout(self, timeout: int) -> None:
        self.set("DiscoverableTimeout", timeout)

    @property
    def discovering(self) -> bool:
        return cast(bool, self.get("Discovering"))

    @property
    def klass(self) -> int:
        return cast(int, self.get("Class"))

    @property
    def name(self) -> str:
        return cast(str, self.get("Name"))

    @property
    def powered(self) -> bool:
        return cast(bool, self.get("Powered"))


class AnyAdapter(AnyBase):
    def __init__(self) -> None:
        super().__init__('org.bluez.Adapter1')
