from typing import Optional, Callable

from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase
from blueman.bluez.errors import BluezDBusException


class Device(Base):
    _interface_name = 'org.bluez.Device1'

    def __init__(self, obj_path: str):
        super().__init__(obj_path=obj_path)

    def pair(
        self,
        reply_handler: Optional[Callable[[], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        self._call('Pair', reply_handler=reply_handler, error_handler=error_handler)

    def connect(  # type: ignore
        self,
        reply_handler: Optional[Callable[[], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        self._call('Connect', reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(  # type: ignore
        self,
        reply_handler: Optional[Callable[[], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)


class AnyDevice(AnyBase):
    def __init__(self) -> None:
        super().__init__('org.bluez.Device1')
