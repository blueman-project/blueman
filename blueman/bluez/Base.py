# coding=utf-8
from gi.repository import Gio, GLib, GObject
from gi.types import GObjectMeta
from blueman.bluez.errors import parse_dbus_error
import logging


class BaseMeta(GObjectMeta):
    def __call__(cls, *args, **kwargs):
        instances = cls.__dict__.get("__instances__")
        if instances is None:
            cls.__instances__ = instances = {}

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

        instance = super().__call__(*args, **kwargs)
        cls.__instances__[interface_name] = {path: instance}

        return instance


class Base(Gio.DBusProxy, metaclass=BaseMeta):
    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __name = 'org.bluez'
    __bus_type = Gio.BusType.SYSTEM

    __gsignals__ = {
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None,
                             (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT))
    }

    def __init__(self, interface_name, obj_path, *args, **kwargs):
        super().__init__(
            g_name=self.__name,
            g_interface_name=interface_name,
            g_object_path=obj_path,
            g_bus_type=self.__bus_type,
            # FIXME See issue 620
            g_flags=Gio.DBusProxyFlags.GET_INVALIDATED_PROPERTIES,
            *args, **kwargs)

        self.init()
        self.__interface_name = interface_name
        self.__fallback = {'Icon': 'blueman', 'Class': 0, 'Appearance': 0}

        self.__variant_map = {str: 's', int: 'u', bool: 'b'}

    def do_g_properties_changed(self, changed_properties, _invalidated_properties):
        changed = changed_properties.unpack()
        object_path = self.get_object_path()
        logging.debug("%s %s" % (object_path, changed))
        for key, value in changed.items():
            self.emit("property-changed", key, value, object_path)

    def _call(self, method, param=None, reply_handler=None, error_handler=None):
        def callback(proxy, result, reply, error):
            try:
                value = proxy.call_finish(result).unpack()
                if reply:
                    reply(*value)
                else:
                    return value
            except GLib.Error as e:
                if error:
                    error(parse_dbus_error(e))
                else:
                    raise parse_dbus_error(e)

        self.call(method, param, Gio.DBusCallFlags.NONE, GLib.MAXINT, None,
                  callback, reply_handler, error_handler)

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
            if name in self.get_cached_property_names():
                return self.get_cached_property(name).unpack()
            elif name in self.__fallback:
                return self.__fallback[name]
            else:
                raise parse_dbus_error(e)

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
