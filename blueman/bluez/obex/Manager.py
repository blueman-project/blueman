# coding=utf-8
import logging
import weakref
from blueman.bluez.obex.Transfer import Transfer
from gi.repository import GObject, Gio
from gi.types import GObjectMeta


class ManagerMeta(GObjectMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)

        return cls._instance


class Manager(GObject.GObject, metaclass=ManagerMeta):
    __gsignals__ = {
        'session-added': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'session-removed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'transfer-started': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        'transfer-completed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez.obex'

    def __init__(self):
        super().__init__()
        self.__transfers = {}
        self.__signals = []

        self._object_manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
            Gio.BusType.SESSION, Gio.DBusObjectManagerClientFlags.NONE,
            self.__bus_name, '/', None, None, None)

        self.__signals.append(self._object_manager.connect('object-added', self._on_object_added))
        self.__signals.append(self._object_manager.connect('object-removed', self._on_object_removed))

        weakref.finalize(self, self._on_delete)

    def _on_delete(self):
        for sig in self.__signals:
            self._object_manager.disconnect(sig)

    def _on_object_added(self, object_manager, dbus_object):
        session_proxy = dbus_object.get_interface('org.bluez.obex.Session1')
        transfer_proxy = dbus_object.get_interface('org.bluez.obex.Transfer1')
        object_path = dbus_object.get_object_path()

        if transfer_proxy:
            logging.info(object_path)
            transfer = Transfer(object_path)
            completed_sig = transfer.connect_signal('completed', self._on_transfer_completed, True)
            error_sig = transfer.connect_signal('error', self._on_transfer_completed, False)
            self.__transfers[object_path] = (transfer, (completed_sig, error_sig))
            self.emit('transfer-started', object_path)

        if session_proxy:
            logging.info(object_path)
            self.emit('session-added', object_path)

    def _on_object_removed(self, object_manager, dbus_object):
        session_proxy = dbus_object.get_interface('org.bluez.obex.Session1')
        transfer_proxy = dbus_object.get_interface('org.bluez.obex.Transfer1')
        object_path = dbus_object.get_object_path()

        if transfer_proxy and object_path in self.__transfers:
            logging.info(object_path)
            transfer, signals = self.__transfers.pop(object_path)

            for sig in signals:
                transfer.disconnect_signal(sig)

        if session_proxy:
            logging.info(object_path)
            self.emit('session-removed', object_path)

    def _on_transfer_completed(self, transfer, success):
        transfer_path = transfer.get_object_path()

        logging.info("%s %s" % (transfer_path, success))
        self.emit('transfer-completed', transfer_path, success)

    @classmethod
    def watch_name_owner(cls, appeared_handler, vanished_handler):
        Gio.bus_watch_name(Gio.BusType.SESSION, cls.__bus_name, Gio.BusNameWatcherFlags.AUTO_START,
                           appeared_handler, vanished_handler)
