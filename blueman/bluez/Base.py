# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository.GObject import GObject
from gi.repository import Gio, GLib
from blueman.bluez.errors import parse_dbus_error


class Base(GObject):
    connect_signal = GObject.connect
    disconnect_signal = GObject.disconnect

    __bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)
    __bus_name = 'org.bluez'

    def __new__(cls, *args, **kwargs):
        instances = cls.__dict__.get("__instances__")
        if instances is None:
            cls.__instances__ = instances = {}

        # ** Below argument parsing has to be kept in sync with _init **
        path = None
        interface_name = None

        if kwargs:
            interface_name = kwargs.get('interface_name')
            path = kwargs.get('obj_path')

        if args:
            for arg in args:
                if args is None:
                    continue
                elif '/' in arg:
                    path = arg
                elif '.' in arg:
                    interface_name = arg

        if not interface_name:
            interface_name = cls._interface_name

        if interface_name in instances:
            if path in instances[interface_name]:
                return instances[interface_name][path]

        instance = super(Base, cls).__new__(cls)
        instance._init(*args, **kwargs)
        cls.__instances__[interface_name] = {path: instance}

        return instance

    def __init__(self, *args, **kwargs):
        pass

    def _init(self, interface_name, obj_path, properties_interface=False):
        self.__signals = []
        self.__obj_path = obj_path
        self.__interface_name = interface_name
        super(Base, self).__init__()

        self.__dbus_proxy = Gio.DBusProxy.new_sync(self.__bus,
            Gio.DBusProxyFlags.NONE, None, self.__bus_name,
            self.__obj_path, self.__interface_name)

        if properties_interface:
            self.__dbus_properties_proxy = Gio.DBusProxy.new_sync(self.__bus,
                Gio.DBusProxyFlags.NONE, None, self.__bus_name,
                self.__obj_path, 'org.freedesktop.DBus.Properties')

    def __del__(self):
        for sig in self.__signals:
            self.__dbus_proxy.disconnect(sig)

    def _call(self, method, param=None, properties=False, *args, **kwargs):
        def callback(proxy, result, reply_handler, error_handler):
            try:
                result = proxy.call_finish(result).unpack()
                reply_handler(*result)
            except GLib.Error as e:
                error_handler(parse_dbus_error(e))

        def ok(*args, **kwargs):
            if callable(reply_handler):
                reply_handler(*args, **kwargs)

        def err(e):
            if callable(error_handler):
                error_handler(e)
            else:
                raise exception

        if properties: dbus_proxy = self.__dbus_properties_proxy
        else: dbus_proxy = self.__dbus_proxy

        if 'reply_handler' in kwargs:
            reply_handler = kwargs.pop('reply_handler')
        else:
            reply_handler = None

        if 'error_handler' in kwargs:
            error_handler = kwargs.pop('error_handler')
        else:
            error_handler = None

        if reply_handler or error_handler:
            # Make sure we have an error handler if we do async calls
            assert(error_handler != None)

            dbus_proxy.call(method, param, Gio.DBusCallFlags.NONE, GLib.MAXINT, None,
                callback, ok, err)
        else:
            try:
                result = dbus_proxy.call_sync(method, param, Gio.DBusCallFlags.NONE,
                                              GLib.MAXINT, None)
                if result:
                    return result.unpack()
            except GLib.Error as e:
                raise parse_dbus_error(e)

    def get_object_path(self):
        return self.__obj_path

    @property
    def _interface_name(self):
        return self.__interface_name

    @property
    def _dbus_proxy(self):
        return self.__dbus_proxy
