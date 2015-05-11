from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.errors import raise_dbus_error, DBusServiceUnknownError
from blueman.main.SignalTracker import SignalTracker
import dbus
from gi.repository.GObject import GObject


class ObexdNotFoundError(Exception):
    pass


class Base(GObject):
    interface_version = None

    @staticmethod
    def get_interface_version():
        if not Base.interface_version:
            obj = dbus.SessionBus().get_object('org.bluez.obex', '/')
            introspection = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable').Introspect()
            if 'org.freedesktop.DBus.ObjectManager' in introspection:
                dprint('Detected BlueZ integrated obexd')
                Base.interface_version = [5]
            elif 'org.bluez.obex.Manager' in introspection:
                dprint('Detected standalone obexd')
                Base.interface_version = [4]
            else:
                raise ObexdNotFoundError('Could not find any compatible version of obexd')

        return Base.interface_version

    def __init__(self, interface_name, obj_path, legacy_client_bus=False):
        self.__signals = SignalTracker()
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        self.__bus = dbus.SessionBus()
        self.__bus_name = 'org.bluez.obex.client' if legacy_client_bus else 'org.bluez.obex'
        self.__dbus_proxy = self.__bus.get_object(self.__bus_name, obj_path, follow_name_owner_changes=True)
        self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)
        super(Base, self).__init__()

    def __del__(self):
        self.__signals.DisconnectAll()

    def _handle_signal(self, handler, signal):
        self.__signals.Handle('dbus', self.__bus, handler, signal, self.__interface_name, self.__bus_name,
                              self.__obj_path)

    @property
    def _interface(self):
        return self.__interface

    @property
    def object_path(self):
        return self.__obj_path
