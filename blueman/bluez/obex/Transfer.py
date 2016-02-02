# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
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
                                    obj_path=transfer_path,
                                    properties_interface=True)

        self.__signals = []
        sig = self._dbus_proxy.connect('g-properties-changed', self._on_properties_changed)
        self.__signals.append(sig)

    def get(self, name):
        param = GLib.Variant('(ss)', (self._interface_name, name))
        prop = self._call('Get', param, True)[0]
        return prop

    def __getattr__(self, name):
        if name in ('filename', 'name', 'session', 'size'):
            return self.get(name.capitalize())

    def _on_properties_changed(self, proxy, changed_properties, _invalidated_properties):
        for name, value in changed_properties.unpack().items():
            dprint(proxy.get_object_path(), name, value)
            if name == 'Transferred':
                self.emit('progress', value)
            elif name == 'Status':
                if value == 'complete':
                    self.emit('completed')
                elif value == 'error':
                    self.emit('error')
