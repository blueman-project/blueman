from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service

DBusGMainLoop(set_as_default=True)

class MethodAlreadyExists(Exception):
    pass


class DbusService(dbus.service.Object):
    def __init__(self, name, path, bus=dbus.SessionBus):
        self.bus = bus()
        self.bus.request_name(name)

        dbus.service.Object.__init__(self, self.bus, path)

    def add_definitions(self, instance):
        setattr(instance, 'locations', self.locations)

        for name, func in self._definitions(instance):
            if name in self.__class__.__dict__:
                raise MethodAlreadyExists

            self._add_wrapper(getattr(instance, name))

        self.__class__._refresh_dbus_registration()

    def _add_wrapper(self, method):
        def wrapper(*args, **kwargs):
            return method(*args[1:], **kwargs)

        wrapper.__name__ = method.__name__

        for key, value in method.__dict__.items():
            if key.startswith('_dbus_'):
                setattr(wrapper, key, value)

        setattr(self.__class__, method.__name__, wrapper)

    def remove_definitions(self, object):
        for name, func in self._definitions(object):
            delattr(self.__class__, name)

        self.__class__._refresh_dbus_registration()

    @classmethod
    def _refresh_dbus_registration(cls):
        cls.__class__.__init__(cls, cls.__name__, cls.__bases__, cls.__dict__)

    @staticmethod
    def _definitions(object):
        for name, func in object.__class__.__dict__.items():
            if getattr(func, '_dbus_is_method', False) or getattr(func, '_dbus_is_signal', False):
                yield name, func
