from blueman.bluez.AnyBase import AnyBase

from blueman.bluez.Base import Base

_INTERFACE = "org.bluez.Battery1"


class Battery(Base):
    _interface_name = _INTERFACE


class AnyBattery(AnyBase):
    def __init__(self) -> None:
        super().__init__(_INTERFACE)
