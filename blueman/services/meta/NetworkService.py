# coding=utf-8
from typing import Optional, Callable

from blueman.Service import Service
from blueman.bluez.Device import Device
from blueman.bluez.Network import Network
from blueman.bluez.errors import BluezDBusException


class NetworkService(Service):
    def __init__(self, device: Device, uuid: str):
        super().__init__(device, uuid)
        self._service = Network(obj_path=device.get_object_path())

    @property
    def available(self) -> bool:
        # This interface is only available after pairing
        paired: bool = self.device["Paired"]
        return paired

    @property
    def connected(self) -> bool:
        if not self.available:
            return False

        connected: bool = self._service["Connected"]
        return connected

    def connect(
        self,
        reply_handler: Optional[Callable[[str], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        self._service.connect(self.uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(
        self,
        reply_handler: Optional[Callable[[], None]] = None,
        error_handler: Optional[Callable[[BluezDBusException], None]] = None,
    ) -> None:
        self._service.disconnect(reply_handler=reply_handler, error_handler=error_handler)
