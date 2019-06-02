# coding=utf-8
import logging
from blueman.bluez.obex.Base import Base
from gi.repository import GObject, GLib


class Client(Base):
    __gsignals__ = {
        'session-failed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    _interface_name = 'org.bluez.obex.Client1'

    def __init__(self):
        super().__init__(interface_name=self._interface_name, obj_path='/org/bluez/obex')

    def create_session(self, dest_addr, source_addr="00:00:00:00:00:00", pattern="opp"):
        def on_session_created(session_path):
            logging.info("%s %s %s %s" % (dest_addr, source_addr, pattern, session_path))

        def on_session_failed(error):
            logging.error("%s %s %s %s" % (dest_addr, source_addr, pattern, error))
            self.emit("session-failed", error)

        v_source_addr = GLib.Variant('s', source_addr)
        v_pattern = GLib.Variant('s', pattern)
        param = GLib.Variant('(sa{sv})', (dest_addr, {"Source": v_source_addr, "Target": v_pattern}))
        self._call('CreateSession', param, reply_handler=on_session_created, error_handler=on_session_failed)

    def remove_session(self, session_path):
        def on_session_removed():
            logging.info(session_path)

        def on_session_remove_failed(error):
            logging.error("%s %s" % (session_path, error))

        param = GLib.Variant('(o)', (session_path,))
        self._call('RemoveSession', param, reply_handler=on_session_removed,
                   error_handler=on_session_remove_failed)
