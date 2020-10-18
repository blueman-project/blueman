from gettext import gettext as _
from typing import Optional, Callable, List, Set

from blueman.main.DBusProxies import AppletService

from blueman.Service import Service, Action, Instance
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
    def connectable(self) -> bool:
        return not self.available or not self._service["Connected"]

    @property
    def connected_instances(self) -> List[Instance]:
        return [] if self.connectable else [Instance(self.name)]

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

    @property
    def common_actions(self) -> Set[Action]:
        def renew() -> None:
            AppletService().DhcpClient('(s)', self.device.get_object_path())

        return {Action(
            _("Renew IP Address"),
            "view-refresh",
            {"DhcpClient"},
            renew
        )}
