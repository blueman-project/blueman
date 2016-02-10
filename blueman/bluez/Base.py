from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from gi.repository.GObject import GObject
from blueman.bluez.errors import parse_dbus_error


class Base(GObject):
    connect_signal = GObject.connect
    disconnect_signal = GObject.disconnect

    __bus = dbus.SystemBus()
    __bus_name = 'org.bluez'

    def __init__(self, interface_name, obj_path):
        self.__signals = []
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        super(Base, self).__init__()
        if obj_path:
            self.__dbus_proxy = self.__bus.get_object(self.__bus_name, obj_path, follow_name_owner_changes=True)
            self.__interface = dbus.Interface(self.__dbus_proxy, interface_name)

    def __del__(self):
        for args in self.__signals:
            self.__bus.remove_signal_receiver(*args)

    def _call(self, method, *args, **kwargs):
        def ok():
            if callable(reply_handler):
                reply_handler()

        def err(e):
            exception = parse_dbus_error(e)
            if callable(error_handler):
                error_handler(exception)
            else:
                raise exception

        if 'interface' in kwargs:
            interface = kwargs.pop('interface')
        else:
            interface = self.__interface

        if 'reply_handler' in kwargs:
            reply_handler = kwargs.pop('reply_handler')
        else:
            reply_handler = None

        if 'error_handler' in kwargs:
            error_handler = kwargs.pop('error_handler')
        else:
            error_handler = None

        # Make sure we have an error handler if we do async calls
        if reply_handler: assert(error_handler != None)

        try:
            if reply_handler or error_handler:
                return getattr(interface, method)(reply_handler=ok, error_handler=err, *args, **kwargs)
            else:
                return getattr(interface, method)(*args, **kwargs)
        except dbus.DBusException as exception:
            raise parse_dbus_error(exception)

    def _handle_signal(self, handler, signal, interface_name=None, object_path=None, path_keyword=None):
        args = (handler, signal, interface_name or self.__interface_name, self.__bus_name,
                object_path or self.__obj_path)
        self.__bus.add_signal_receiver(*args, path_keyword=path_keyword)
        self.__signals.append(args)

    def get_object_path(self):
        return self.__obj_path

    @property
    def _interface_name(self):
        return self.__interface_name

    @property
    def _dbus_proxy(self):
        return self.__dbus_proxy
