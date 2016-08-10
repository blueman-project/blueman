# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio, GLib, GObject
from blueman.bluez.errors import parse_dbus_error, BluezDBusException
from blueman.Functions import dprint
import sys


class Base(Gio.DBusProxy):
    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __name = 'org.bluez'
    __bus_type = Gio.BusType.SYSTEM

    __gsignals__ = {
        str('property-changed'): (GObject.SignalFlags.NO_HOOKS, None,
                                  (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT))
    }

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

    def _init(self, interface_name, obj_path, *args, **kwargs):
        super(Base, self).__init__(
            g_name=self.__name,
            g_interface_name=interface_name,
            g_object_path=obj_path,
            g_bus_type=self.__bus_type,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs)

        self.init()
        self.__interface_name = interface_name
        self.__fallback = {'Icon': 'blueman', 'Class': None}

        if sys.version_info.major < 3:
            self.__variant_map = {str: 's', unicode: 's', int: 'u', bool: 'b'}
        else:
            self.__variant_map = {str: 's', int: 'u', bool: 'b'}

    def do_g_properties_changed(self, changed_properties, _invalidated_properties):
        for key, value in changed_properties.unpack().items():
            path = self.get_object_path()
            dprint(path, key, value)
            self.emit("property-changed", key, value, path)

    def _call(self, method, param=None, *args, **kwargs):
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
                raise e

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

            self.call(method, param, Gio.DBusCallFlags.NONE, GLib.MAXINT, None,
                      callback, ok, err)
        else:
            try:
                result = self.call_sync(method, param, Gio.DBusCallFlags.NONE,
                                        GLib.MAXINT, None)
                if result:
                    return result.unpack()
            except GLib.Error as e:
                raise parse_dbus_error(e)

    def get(self, name):
        try:
            prop = self.call_sync(
                'org.freedesktop.DBus.Properties.Get',
                GLib.Variant('(ss)', (self._interface_name, name)),
                Gio.DBusCallFlags.NONE,
                GLib.MAXINT,
                None)
            return prop.unpack()[0]
        except GLib.Error as e:
            if name in self.__fallback:
                return self.__fallback[name]
            else:
                raise e

    def set(self, name, value):
        v = GLib.Variant(self.__variant_map[type(value)], value)
        param = GLib.Variant('(ssv)', (self._interface_name, name, v))
        self.call('org.freedesktop.DBus.Properties.Set',
                  param,
                  Gio.DBusCallFlags.NONE,
                  GLib.MAXINT,
                  None)

    def get_properties(self):
        param = GLib.Variant('(s)', (self._interface_name,))
        res = self.call_sync('org.freedesktop.DBus.Properties.GetAll',
                             param,
                             Gio.DBusCallFlags.NONE,
                             GLib.MAXINT,
                             None)

        props = res.unpack()[0]
        for k, v in self.__fallback.items():
            if k in props:
                continue
            else:
                props[k] = v

        return props

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.get_properties()
