# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.DBusServiceObject import *
from gi.repository import Gio
from blueman.Functions import dprint

class MethodAlreadyExists(Exception):
    pass


class DbusService(DBusServiceObject):
    def __init__(self, bus_name, path, **kwargs):
        super(DbusService, self).__init__(object_path=path, **kwargs)
        self.__bus_name = bus_name

    def _on_name_acquired(self, conn, name):
        dprint('Got bus name: %s' % name)

    def connect_bus(self):
        self.bus_id = Gio.bus_own_name_on_connection(self.connection, self.__bus_name,
                                                     Gio.BusNameOwnerFlags.NONE,
                                                     self._on_name_acquired,
                                                     None)

    def disconnect_bus(self):
        if self.bus_id:
            Gio.bus_unown_name(self.bus_id)

        self.bus_id = 0

    def add_definitions(self, instance):
        for name, func in self._definitions(instance):
            if name in self.__class__.__dict__:
                raise MethodAlreadyExists

            self._add_wrapper(getattr(instance, name))

        self._refresh()
        self.__class__._refresh_dbus_registration()

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

        self._refresh()
        self.__class__._refresh_dbus_registration()

    @classmethod
    def _refresh_dbus_registration(cls):
        cls.__class__.__init__(cls, cls.__name__, cls.__bases__, cls.__dict__)

    @staticmethod
    def _definitions(obj):
        for name, func in obj.__class__.__dict__.items():
            if hasattr(func, '_dbus_info'):
                yield name, func
