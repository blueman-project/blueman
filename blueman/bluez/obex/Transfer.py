# coding=utf-8
import logging
from blueman.bluez.obex.Base import Base
from gi.repository import GObject, GLib


class Transfer(Base):
    __gsignals__ = {
        str('progress'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('completed'): (GObject.SignalFlags.NO_HOOKS, None, ()),
        str('error'): (GObject.SignalFlags.NO_HOOKS, None, ())
    }

    _interface_name = 'org.bluez.obex.Transfer1'

    def _init(self, transfer_path):
        super(Transfer, self)._init(interface_name=self._interface_name,
                                    obj_path=transfer_path)

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
