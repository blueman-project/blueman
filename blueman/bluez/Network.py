from collections.abc import Callable
from typing import cast
from blueman.bluemantyping import ObjectPath

from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase
from gi.repository import GLib

from blueman.bluez.errors import BluezDBusException


class Network(Base):
    _interface_name = 'org.bluez.Network1'

    def __init__(self, obj_path: ObjectPath):
        super().__init__(obj_path=obj_path)

    def connect(  # type: ignore
        self,
        uuid: str,
        reply_handler: Callable[[str], None] | None = None,
        error_handler: Callable[[BluezDBusException], None] | None = None,
    ) -> None:
        param = GLib.Variant('(s)', (uuid,))
        self._call('Connect', param, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(  # type: ignore
        self,
        reply_handler: Callable[[], None] | None = None,
        error_handler: Callable[[BluezDBusException], None] | None = None,
    ) -> None:
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)

    @property
    def connected(self) -> bool:
        return cast(bool, self.get("Connected"))

    @property
    def interface(self) -> str:
        return cast(str, self.get("Interface"))


class AnyNetwork(AnyBase):
    def __init__(self) -> None:
        super().__init__('org.bluez.Network1')
