# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Transfer import Transfer
from blueman.bluez.ManagerBase import ManagerBase
from gi.repository import GObject, Gio


class Manager(ManagerBase):
    __gsignals__ = {
        str('session-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('transfer-started'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('transfer-completed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    __bus_name = 'org.bluez.obex'
    __bus_type = Gio.BusType.SESSION

    def _init(self):
        super(Manager, self)._init()
        self.__transfers = {}
        self.__signals = []

    def _on_object_added(self, object_manager, dbus_object):
        transfer_proxy = dbus_object.get_interface('org.bluez.obex.Transfer1')

        if transfer_proxy:
            transfer_path = transfer_proxy.get_object_path()
            transfer = Transfer(transfer_path)
            completed_sig = transfer.connect_signal('completed', self._on_transfer_completed, True)
            error_sig = transfer.connect_signal('error', self._on_transfer_completed, False)
            self.__signals[transfer_path] = (completed_sig, error_sig)

            dprint(transfer_path)
            self.emit('transfer-started', transfer_path)

    def _on_object_removed(self, object_manager, dbus_object):
        session_proxy = dbus_object.get_interface('org.bluez.obex.Session1')

        if session_proxy:
            session_path = session_proxy.get_object_path()
            dprint(session_path)
            self.emit('session-removed', session_path)

    def _on_transfer_completed(self, transfer, success):
        transfer_path = transfer.get_object_path()
        signals = self.__transfers.pop(transfer_path)
        for sig in signals:
            transfer.disconnect_signal(sig)

        dprint(transfer_path, success)
        self.emit('transfer-completed', transfer_path, success)
