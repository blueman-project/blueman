from collections.abc import Callable
from typing import cast
from blueman.bluemantyping import ObjectPath, BtAddress

from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase
from blueman.bluez.errors import BluezDBusException


class Device(Base):
    _interface_name = 'org.bluez.Device1'

    def __init__(self, obj_path: ObjectPath):
        super().__init__(obj_path=obj_path)

    def pair(
        self,
        reply_handler: Callable[[], None] | None = None,
        error_handler: Callable[[BluezDBusException], None] | None = None,
    ) -> None:
        self._call('Pair', reply_handler=reply_handler, error_handler=error_handler)

    def connect(  # type: ignore
        self,
        reply_handler: Callable[[], None] | None = None,
        error_handler: Callable[[BluezDBusException], None] | None = None,
    ) -> None:
        self._call('Connect', reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(  # type: ignore
        self,
        reply_handler: Callable[[], None] | None = None,
        error_handler: Callable[[BluezDBusException], None] | None = None,
    ) -> None:
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)

    @property
    def address(self) -> BtAddress:
        return cast(BtAddress, self.get("Address"))

    @property
    def alias(self) -> str:
        return cast(str, self.get("Alias"))

    @property
    def adapter(self) -> ObjectPath:
        return cast(ObjectPath, self.get("Adapter"))

    @property
    def appearance(self) -> int:
        return cast(int, self.get("Appearance"))

    @property
    def blocked(self) -> bool:
        return cast(bool, self.get("Blocked"))

    @blocked.setter
    def blocked(self, v: bool) -> None:
        self.set("Blocked", v)

    @property
    def bonded(self) -> bool:
        return cast(bool, self.get("Appearance"))

    @property
    def connected(self) -> bool:
        return cast(bool, self.get("Connected"))

    @property
    def icon(self) -> str:
        return cast(str, self.get("Icon"))

    @property
    def klass(self) -> int:
        return cast(int, self.get("Class"))

    @property
    def name(self) -> str | None:
        try:
            return cast(str, self.get("Name"))
        except BluezDBusException:
            return None

    @property
    def paired(self) -> bool:
        return cast(bool, self.get("Paired"))

    @property
    def trusted(self) -> bool:
        return cast(bool, self.get("Trusted"))

    @trusted.setter
    def trusted(self, v: bool) -> None:
        self.set("Trusted", v)

    @property
    def uuids(self) -> list[str]:
        return cast(list[str], self.get("UUIDs"))

    @property
    def display_name(self) -> str:
        alias: str = self.alias
        return alias.strip()


class AnyDevice(AnyBase):
    def __init__(self) -> None:
        super().__init__('org.bluez.Device1')
