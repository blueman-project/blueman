from typing import Optional, Callable

from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase
from gi.repository import GLib

from blueman.bluez.errors import BluezDBusException


class Network(Base):
    _interface_name = 'org.bluez.Network1'

    def __init__(self, obj_path: str):
        super().__init__(obj_path=obj_path)

    def connect(  # type: ignore
        self,
        uuid: str,
        reply_handler: Optional[Callable[[str], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        param = GLib.Variant('(s)', (uuid,))
        self._call('Connect', param, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(  # type: ignore
        self,
        reply_handler: Optional[Callable[[], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)


class AnyNetwork(AnyBase):
    def __init__(self) -> None:
        super().__init__('org.bluez.Network1')
