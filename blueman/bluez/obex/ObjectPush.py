import logging
from typing import Dict

from blueman.bluez.errors import BluezDBusException
from blueman.bluez.obex.Base import Base
from gi.repository import GObject, GLib

from blueman.bluemantyping import GSignals


class ObjectPush(Base):
    __gsignals__: GSignals = {
        'transfer-started': (GObject.SignalFlags.NO_HOOKS, None, (str, str,)),
        'transfer-failed': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
    }

    _interface_name = 'org.bluez.obex.ObjectPush1'

    def __init__(self, obj_path: str):
        super().__init__(obj_path=obj_path)

    def send_file(self, file_path: str) -> None:
        def on_transfer_started(transfer_path: str, props: Dict[str, str]) -> None:
            logging.info(" ".join((self.get_object_path(), file_path, transfer_path)))
            self.emit('transfer-started', transfer_path, props['Filename'])

        def on_transfer_error(error: BluezDBusException) -> None:
            logging.error(f"{file_path} {error}")
            self.emit('transfer-failed', error)

        param = GLib.Variant('(s)', (file_path,))
        self._call('SendFile', param, reply_handler=on_transfer_started, error_handler=on_transfer_error)

    def get_session_path(self) -> str:
        path: str = self.get_object_path()
        return path
