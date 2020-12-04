import logging
from typing import List, Optional

from blueman.bluez.obex.Base import Base
from gi.repository import GObject, GLib

from blueman.bluemantyping import GSignals


class Transfer(Base):
    __gsignals__: GSignals = {
        'progress': (GObject.SignalFlags.NO_HOOKS, None, (int,)),
        'completed': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'error': (GObject.SignalFlags.NO_HOOKS, None, ())
    }

    _interface_name = 'org.bluez.obex.Transfer1'

    def __init__(self, obj_path: str):
        super().__init__(obj_path=obj_path)

    @property
    def filename(self) -> Optional[str]:
        name: Optional[str] = self.get("Filename")
        return name

    @property
    def name(self) -> str:
        name: str = self.get("Name")
        return name

    @property
    def session(self) -> str:
        session: str = self.get("Session")
        return session

    @property
    def size(self) -> Optional[int]:
        size: Optional[int] = self.get("Size")
        return size

    def do_g_properties_changed(self, changed_properties: GLib.Variant, _invalidated_properties: List[str]) -> None:
        for name, value in changed_properties.unpack().items():
            logging.debug(f"{self.get_object_path()} {name} {value}")
            if name == 'Transferred':
                self.emit('progress', value)
            elif name == 'Status':
                if value == 'complete':
                    self.emit('completed')
                elif value == 'error':
                    self.emit('error')
