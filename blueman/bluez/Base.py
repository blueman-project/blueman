from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from gi.repository.GObject import GObject


class Base(GObject):
    connect_signal = GObject.connect
    disconnect_signal = GObject.disconnect

    def __init__(self, interface_name, obj_path):
        self.__signals = []
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        self.__bus = dbus.SystemBus()
        super(Base, self).__init__()
        if obj_path:
            self.__dbus_proxy = self.__bus.get_object('org.bluez', obj_path, follow_name_owner_changes=True)
            self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)

    def __del__(self):
        for args in self.__signals:
            self.__bus.remove_signal_receiver(*args)

    def _handle_signal(self, handler, signal, interface_name=None, object_path=None):
        args = (handler, signal, interface_name or self.__interface_name, 'org.bluez', object_path or self.__obj_path)
        self.__bus.add_signal_receiver(*args)
        self.__signals.append(args)

    def get_object_path(self):
        return self.__obj_path

    @property
    def _interface_name(self):
        return self.__interface_name

    @property
    def _dbus_proxy(self):
        return self.__dbus_proxy

    @property
    def _interface(self):
        return self.__interface
