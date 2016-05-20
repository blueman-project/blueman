# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject, Gio, GLib
from blueman.Functions import dprint
from blueman.bluez.Base import Base
from blueman.bluez.errors import BluezDBusException

import sys

class PropertiesBase(Base):
    __gsignals__ = {
        str('property-changed'): (GObject.SignalFlags.NO_HOOKS, None,
                                  (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT))
    }

    _interface_name = 'org.bluez.NetworkServer1'

    if sys.version_info.major < 3:
        __variant_map = {str: 's', unicode: 's', int: 'u', bool: 'b'}
    else:
        __variant_map = {str: 's', int: 'u', bool: 'b'}

    def _init(self, interface_name, obj_path):
        super(PropertiesBase, self)._init(interface_name=self._interface_name,
                                          obj_path=obj_path,
                                          properties_interface=True)
        self.__signals = []

        self.__fallback = {'Icon': 'blueman', 'Class': None}

        sig = self._dbus_proxy.connect("g-properties-changed", self._on_properties_changed)
        self.__signals.append(sig)

    def _on_properties_changed(self, proxy, changed_properties, _invalidated_properties):
        for key, value in changed_properties.unpack().items():
            path = proxy.get_object_path()
            dprint(path, key, value)
            self.emit("property-changed", key, value, path)

    def get(self, name):
        prop = self._dbus_proxy.get_cached_property(name)

        if prop is not None:
            return prop.unpack()
        elif not prop and name in self.__fallback:
            return self.__fallback[name]
        else:
            raise BluezDBusException("No such property '%s'" % name)

    def set(self, name, value):
        v = GLib.Variant(self.__variant_map[type(value)], value)
        param = GLib.Variant('(ssv)', (self._interface_name, name, v))
        self._call('Set', param, True)

    def get_properties(self):
        prop_names = self._dbus_proxy.get_cached_property_names()
        result = {}
        for name in prop_names:
            result[name] = self._dbus_proxy.get_cached_property(name).unpack()

        if result:
            for k, v in self.__fallback.items():
                if k in result: continue
                else: result[k] = v

            return result

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.get_properties()
