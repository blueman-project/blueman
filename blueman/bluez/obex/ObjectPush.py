# coding=utf-8
import logging
from blueman.bluez.obex.Base import Base
from gi.repository import GObject, GLib


class ObjectPush(Base):
    __gsignals__ = {
        'transfer-started': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        'transfer-failed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    _interface_name = 'org.bluez.obex.ObjectPush1'

    def __init__(self, session_path):
        super().__init__(interface_name=self._interface_name, obj_path=session_path)

    def send_file(self, file_path):
        def on_transfer_started(transfer_path, props):
            logging.info(" ".join((self.get_object_path(), file_path, transfer_path)))
            self.emit('transfer-started', transfer_path, props['Filename'])

        def on_transfer_error(error):
            logging.error("%s %s" % (file_path, error))
            self.emit('transfer-failed', error)

        param = GLib.Variant('(s)', (file_path,))
        self._call('SendFile', param, reply_handler=on_transfer_started, error_handler=on_transfer_error)

    def get_session_path(self):
        return self.get_object_path()
