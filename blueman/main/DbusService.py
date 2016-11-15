# coding=utf-8
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

        super(DbusService, self).__init__(self.bus, path)

    def add_definitions(self, instance):
        setattr(instance, 'locations', list(self.locations))

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
            if key.startswith('_dbus_'):
                setattr(wrapper, key, value)

        setattr(self.__class__, method.__name__, wrapper)

    def remove_definitions(self, obj):
        for name, func in self._definitions(obj):
            delattr(self.__class__, name)

        self._refresh_dbus_registration()

    @staticmethod
    def _definitions(obj):
        for name, func in obj.__class__.__dict__.items():
            if getattr(func, '_dbus_is_method', False) or getattr(func, '_dbus_is_signal', False):
                yield name, func
