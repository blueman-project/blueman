# coding=utf-8
from blueman.main.DBusServiceObject import DBusServiceObject, DBusMethodInfo, DBusSignalInfo
from gi.repository import Gio
import logging


class MethodAlreadyExists(Exception):
    pass


class DbusService(DBusServiceObject):
    def __init__(self, bus_name, path, **kwargs):
        super(DbusService, self).__init__(object_path=path, **kwargs)
        self.__bus_name = bus_name
        self._bus_id = None

    def _on_name_acquired(self, conn, name):
        logging.debug('Got bus name: %s' % name)

    def connect_bus(self):
        self._bus_id = Gio.bus_own_name_on_connection(self.connection, self.__bus_name,
                                                      Gio.BusNameOwnerFlags.NONE,
                                                      self._on_name_acquired,
                                                      None)

    def disconnect_bus(self):
        if self._bus_id:
            Gio.bus_unown_name(self.bus_id)

        self._bus_id = None

    def add_definitions(self, instance):
        for name, func in self._definitions(instance):
            if name in self.__class__.__dict__:
                raise MethodAlreadyExists

            self._add_wrapper(getattr(instance, name))

        self._refresh_dbus_registration()

    def _add_wrapper(self, method):
        def wrapper(*args, **kwargs):
            return method(*args[1:], **kwargs)

        wrapper.__name__ = method.__name__

        for key, value in method.__dict__.items():
            if key == '_dbus_info':
                setattr(wrapper, key, value)

        setattr(self.__class__, method.__name__, wrapper)

    def remove_definitions(self, obj):
        for name, func in self._definitions(obj):
            delattr(self.__class__, name)

        self._refresh_dbus_registration()

    @staticmethod
    def _definitions(obj):
        for name, func in obj.__class__.__dict__.items():
            dbus_info = getattr(func, "_dbus_info", None)
            if isinstance(dbus_info, DBusMethodInfo) or isinstance(dbus_info, DBusSignalInfo):
                yield name, func
