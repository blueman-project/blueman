from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from gi.repository.GObject import GObject


class Base(GObject):
    def __init__(self, interface_name, obj_path):
        self.__signals = []
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        self.__bus = dbus.SessionBus()
        self.__dbus_proxy = self.__bus.get_object('org.bluez.obex', obj_path, follow_name_owner_changes=True)
        self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)
        super(Base, self).__init__()

    def __del__(self):
        for args in self.__signals:
            self.__bus.remove_signal_receiver(*args)

    def _handle_signal(self, handler, signal):
        args = (handler, signal, self.__interface_name, 'org.bluez.obex', self.__obj_path)
        self.__bus.add_signal_receiver(*args)
        self.__signals.append(args)

    @property
    def _interface(self):
        return self.__interface

    @property
    def object_path(self):
        return self.__obj_path
