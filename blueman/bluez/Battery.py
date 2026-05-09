from typing import cast
from blueman.bluez.AnyBase import AnyBase

from blueman.bluez.Base import Base

_INTERFACE = "org.bluez.Battery1"


class Battery(Base):
    _interface_name = _INTERFACE

    @property
    def percentage(self) -> int:
        return cast(int, self.get("Percentage"))

    @property
    def source(self) -> str:
        return cast(str, self.get("Source"))


class AnyBattery(AnyBase):
    def __init__(self) -> None:
        super().__init__(_INTERFACE)
