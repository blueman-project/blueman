# coding=utf-8
import logging
from blueman.bluez.obex.Base import Base
from gi.repository import GObject


class Transfer(Base):
    __gsignals__ = {
        'progress': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'completed': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'error': (GObject.SignalFlags.NO_HOOKS, None, ())
    }

    _interface_name = 'org.bluez.obex.Transfer1'

    def __init__(self, transfer_path):
        super().__init__(interface_name=self._interface_name, obj_path=transfer_path)

    def __getattr__(self, name):
        if name in ('filename', 'name', 'session', 'size'):
            return self.get(name.capitalize())

    def do_g_properties_changed(self, changed_properties, _invalidated_properties):
        for name, value in changed_properties.unpack().items():
            logging.debug("%s %s %s" % (self.get_object_path(), name, value))
            if name == 'Transferred':
                self.emit('progress', value)
            elif name == 'Status':
                if value == 'complete':
                    self.emit('completed')
                elif value == 'error':
                    self.emit('error')
