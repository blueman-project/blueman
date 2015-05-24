from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.SignalTracker import SignalTracker
import dbus
from gi.repository.GObject import GObject


class Base(GObject):
    def __init__(self, interface_name, obj_path):
        self.__signals = SignalTracker()
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        self.__bus = dbus.SessionBus()
        self.__dbus_proxy = self.__bus.get_object('org.bluez.obex', obj_path, follow_name_owner_changes=True)
        self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)
        super(Base, self).__init__()

    def __del__(self):
        self.__signals.DisconnectAll()

    def _handle_signal(self, handler, signal):
        self.__signals.Handle('dbus', self.__bus, handler, signal, self.__interface_name, 'org.bluez.obex',
                              self.__obj_path)

    @property
    def _interface(self):
        return self.__interface

    @property
    def object_path(self):
        return self.__obj_path
