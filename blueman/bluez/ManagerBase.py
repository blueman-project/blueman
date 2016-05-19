# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from gi.repository import GObject, Gio
from blueman.Functions import dprint

from blueman.bluez.Adapter import Adapter
from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import DBusNoSuchAdapterError


class ManagerBase(GObject.GObject):
    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez'
    __bus_type = Gio.BusType.SYSTEM
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ManagerBase, cls).__new__(cls)
            cls._instance._init(*args, **kwargs)
        return cls._instance

    def __init__(self, *args, **kwargs):
        pass

    def __del__(self):
        for sig in self.__signals:
            self._object_manager.disconnect(sig)

    def _init(self):
        super(ManagerBase, self).__init__()
        self.__signals = []

        self._object_manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
            self.__bus_type, Gio.DBusObjectManagerClientFlags.NONE,
            self.__bus_name, '/', None, None, None)

        self.__signals.append(self._object_manager.connect('object-added', self._on_object_added))
        self.__signals.append(self._object_manager.connect('object-removed', self._on_object_removed))

    def _on_object_added(self, object_manager, dbus_object):
        # Override in subclass
        pass

    def _on_object_removed(self, object_manager, dbus_object):
        # Override in subclass
        pass

    @classmethod
    def watch_name_owner(cls, appeared_handler, vanished_handler):
        Gio.bus_watch_name(cls.__bus_type, cls.__bus_name, Gio.BusNameWatcherFlags.AUTO_START,
                           appeared_handler, vanished_handler)
