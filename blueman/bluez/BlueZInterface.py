from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from blueman.Functions import dprint


class BlueZInterface(object):
    interface_version = None

    @staticmethod
    def get_interface_version():
        if not BlueZInterface.interface_version:
            obj = dbus.SystemBus().get_object('org.bluez', '/')
            introspection = dbus.Interface(obj, 'org.freedesktop.DBus.Introspectable').Introspect()
            if 'org.freedesktop.DBus.ObjectManager' in introspection:
                dprint('Detected BlueZ 5')
                BlueZInterface.interface_version = [5]
            elif 'org.bluez.Manager' in introspection:
                dprint('Detected BlueZ 4')
                BlueZInterface.interface_version = [4]
            else:
                raise Exception('Could not find any compatible version of BlueZ')

        return BlueZInterface.interface_version

    def __init__(self, interface_name, obj_path):
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        self.__bus = dbus.SystemBus()
        if obj_path:
            self.__dbus_proxy = self.__bus.get_object('org.bluez', obj_path, follow_name_owner_changes=True)
            self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)

    def get_object_path(self):
        return self.__obj_path

    def get_interface_name(self):
        return self.__interface_name

    def get_bus(self):
        return self.__bus

    def get_dbus_proxy(self):
        return self.__dbus_proxy

    def get_interface(self):
        return self.__interface
