from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Base import Base
from gi.repository import GObject


class ObjectPush(Base):
    __gsignals__ = {
        str('transfer-started'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        str('transfer-failed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, session_path):
        if self.__class__.get_interface_version()[0] < 5:
            super(ObjectPush, self).__init__('org.bluez.obex.ObjectPush', session_path, True)
        else:
            super(ObjectPush, self).__init__('org.bluez.obex.ObjectPush1', session_path)

    def send_file(self, file_path):
        def on_transfer_started(*params):
            transfer_path, props = params[0] if self.__class__.get_interface_version()[0] < 5 else params
            dprint(self.object_path, file_path, transfer_path)
            self.emit('transfer-started', transfer_path, props['Filename'])

        def on_transfer_error(error):
            dprint(file_path, error)
            self.emit('transfer-failed', error)

        self._interface.SendFile(file_path, reply_handler=on_transfer_started, error_handler=on_transfer_error)

    def get_session_path(self):
        return self.object_path
