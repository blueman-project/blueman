import logging

from blueman.bluez.errors import BluezDBusException
from blueman.bluez.obex.Base import Base
from gi.repository import GObject, GLib

from blueman.bluemantyping import GSignals


class Client(Base):
    __gsignals__: GSignals = {
        'session-failed': (GObject.SignalFlags.NO_HOOKS, None, (object,)),
    }

    _interface_name = 'org.bluez.obex.Client1'
    _obj_path = '/org/bluez/obex'

    def __init__(self) -> None:
        super().__init__(obj_path=self._obj_path)

    def create_session(self, dest_addr: str, source_addr: str = "00:00:00:00:00:00", pattern: str = "opp") -> None:
        def on_session_created(session_path: str) -> None:
            logging.info(f"{dest_addr} {source_addr} {pattern} {session_path}")

        def on_session_failed(error: BluezDBusException) -> None:
            logging.error(f"{dest_addr} {source_addr} {pattern} {error}")
            self.emit("session-failed", error)

        v_source_addr = GLib.Variant('s', source_addr)
        v_pattern = GLib.Variant('s', pattern)
        param = GLib.Variant('(sa{sv})', (dest_addr, {"Source": v_source_addr, "Target": v_pattern}))
        self._call('CreateSession', param, reply_handler=on_session_created, error_handler=on_session_failed)

    def remove_session(self, session_path: str) -> None:
        def on_session_removed() -> None:
            logging.info(session_path)

        def on_session_remove_failed(error: BluezDBusException) -> None:
            logging.error(f"{session_path} {error}")

        param = GLib.Variant('(o)', (session_path,))
        self._call('RemoveSession', param, reply_handler=on_session_removed,
                   error_handler=on_session_remove_failed)
