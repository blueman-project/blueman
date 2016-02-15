from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Transfer import Transfer
from blueman.bluez.obex.Base import Base
from gi.repository import GObject


class Manager(Base):
    __gsignals__ = {
        str('session-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('transfer-started'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('transfer-completed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    def __init__(self):
        if self.__class__.get_interface_version()[0] < 5:
            super(Manager, self).__init__('org.bluez.obex.Manager', '/')
            handlers = {
                'SessionRemoved': self._on_session_removed,
                'TransferStarted': self._on_transfer_started,
                'TransferCompleted': self._on_transfer_completed
            }

            for signal, handler in handlers.items():
                self._handle_signal(handler, signal, )

        else:
            super(Manager, self).__init__('org.freedesktop.DBus.ObjectManager', '/')

            self._transfers = {}

            def on_interfaces_added(object_path, interfaces):
                if 'org.bluez.obex.Transfer1' in interfaces:
                    def on_tranfer_completed(_transfer):
                        self._on_transfer_completed(object_path, True)

                    def on_tranfer_error(_transfer, _msg):
                        self._on_transfer_completed(object_path, False)

                    self._transfers[object_path] = Transfer(object_path)
                    self._transfers[object_path].connect('completed', on_tranfer_completed)
                    self._transfers[object_path].connect('error', on_tranfer_error)
                    self._on_transfer_started(object_path)

            self._handle_signal(on_interfaces_added, 'InterfacesAdded')

            def on_interfaces_removed(object_path, interfaces):
                if 'org.bluez.obex.Session1' in interfaces:
                    self._on_session_removed(object_path)

            self._handle_signal(on_interfaces_removed, 'InterfacesRemoved')

    def _on_session_removed(self, session_path):
        dprint(session_path)
        self.emit('session-removed', session_path)

    def _on_transfer_started(self, transfer_path):
        dprint(transfer_path)
        self.emit('transfer-started', transfer_path)

    def _on_transfer_completed(self, transfer_path, success):
        dprint(transfer_path, success)
        self.emit('transfer-completed', transfer_path, success)
