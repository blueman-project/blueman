import logging
import weakref
from typing import Dict, Callable, List, Tuple

from gi.repository import GObject, Gio

from blueman.bluez.obex.Transfer import Transfer
from blueman.gobject import SingletonGObjectMeta
from blueman.bluemantyping import GSignals


class Manager(GObject.GObject, metaclass=SingletonGObjectMeta):
    __gsignals__: GSignals = {
        'session-added': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'session-removed': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'transfer-started': (GObject.SignalFlags.NO_HOOKS, None, (str,)),
        'transfer-completed': (GObject.SignalFlags.NO_HOOKS, None, (str, bool)),
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez.obex'

    def __init__(self) -> None:
        super().__init__()
        self.__transfers: Dict[str, Tuple[Transfer, Tuple[int, ...]]] = {}

        self._object_manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
            Gio.BusType.SESSION, Gio.DBusObjectManagerClientFlags.NONE,
            self.__bus_name, '/', None, None, None)

        self._manager_handlerids: List[int] = []
        self._manager_handlerids.append(self._object_manager.connect('object-added', self._on_object_added))
        self._manager_handlerids.append(self._object_manager.connect('object-removed', self._on_object_removed))

        weakref.finalize(self, self._on_delete)

    def _on_delete(self) -> None:
        for handlerid in self._manager_handlerids:
            self._object_manager.disconnect(handlerid)
        self._manager_handlerids = []

    def _on_object_added(self, _object_manager: Gio.DBusObjectManager, dbus_object: Gio.DBusObject) -> None:
        session_proxy = dbus_object.get_interface('org.bluez.obex.Session1')
        transfer_proxy = dbus_object.get_interface('org.bluez.obex.Transfer1')
        object_path = dbus_object.get_object_path()

        if transfer_proxy:
            logging.info(object_path)
            transfer = Transfer(obj_path=object_path)
            chandlerid = transfer.connect_signal('completed', self._on_transfer_completed, True)
            ehandlerid = transfer.connect_signal('error', self._on_transfer_completed, False)
            self.__transfers[object_path] = (transfer, (chandlerid, ehandlerid))
            self.emit('transfer-started', object_path)

        if session_proxy:
            logging.info(object_path)
            self.emit('session-added', object_path)

    def _on_object_removed(self, _object_manager: Gio.DBusObjectManager, dbus_object: Gio.DBusObject) -> None:
        session_proxy = dbus_object.get_interface('org.bluez.obex.Session1')
        transfer_proxy = dbus_object.get_interface('org.bluez.obex.Transfer1')
        object_path = dbus_object.get_object_path()

        if transfer_proxy and object_path in self.__transfers:
            logging.info(object_path)
            transfer, handlerids = self.__transfers.pop(object_path)

            for handlerid in handlerids:
                transfer.disconnect_signal(handlerid)

        if session_proxy:
            logging.info(object_path)
            self.emit('session-removed', object_path)

    def _on_transfer_completed(self, transfer: Transfer, success: bool) -> None:
        transfer_path = transfer.get_object_path()

        logging.info(f"{transfer_path} {success}")
        self.emit('transfer-completed', transfer_path, success)

    @classmethod
    def watch_name_owner(
        cls,
        appeared_handler: Callable[[Gio.DBusConnection, str, str], None],
        vanished_handler: Callable[[Gio.DBusConnection, str], None],
    ) -> None:
        Gio.bus_watch_name(Gio.BusType.SESSION, cls.__bus_name, Gio.BusNameWatcherFlags.AUTO_START,
                           appeared_handler, vanished_handler)
