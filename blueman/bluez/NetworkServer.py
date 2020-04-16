from blueman.bluez.Base import Base
from gi.repository import GLib


class NetworkServer(Base):
    _interface_name = 'org.bluez.NetworkServer1'

    def __init__(self, obj_path: str):
        super().__init__(obj_path=obj_path)

    def register(self, uuid: str, bridge: str) -> None:
        param = GLib.Variant('(ss)', (uuid, bridge))
        self._call('Register', param)

    def unregister(self, uuid: str) -> None:
        param = GLib.Variant('(s)', (uuid,))
        self._call('Unregister', param)
