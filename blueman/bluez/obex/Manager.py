# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Transfer import Transfer
from gi.repository import GObject, Gio


class Manager(Gio.DBusObjectManagerClient):
    __gsignals__ = {
        str('session-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('transfer-started'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('transfer-completed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez.obex'
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Manager, cls).__new__(cls)
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    def _init(self):
        super(Manager, self).__init__(
            bus_type=Gio.BusType.SESSION,
            flags=Gio.DBusObjectManagerClientFlags.NONE,
            name=self.__bus_name,
            object_path='/')

        self.init()
        self.__transfers = {}

    def do_object_added(self, dbus_object):
        transfer_proxy = dbus_object.get_interface('org.bluez.obex.Transfer1')

        if transfer_proxy:
            transfer_path = transfer_proxy.get_object_path()
            transfer = Transfer(transfer_path)
            completed_sig = transfer.connect_signal('completed', self._on_transfer_completed, True)
            error_sig = transfer.connect_signal('error', self._on_transfer_completed, False)
            self.__transfers[transfer_path] = (completed_sig, error_sig)

            dprint(transfer_path)
            self.emit('transfer-started', transfer_path)

    def do_object_removed(self, dbus_object):
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

    @classmethod
    def watch_name_owner(cls, appeared_handler, vanished_handler):
        Gio.bus_watch_name(Gio.BusType.SESSION, cls.__bus_name, Gio.BusNameWatcherFlags.AUTO_START,
                           appeared_handler, vanished_handler)
