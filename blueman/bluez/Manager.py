from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from gi.repository import GObject
from blueman.Functions import dprint

from blueman.bluez.Adapter import Adapter
from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error, DBusNoSuchAdapterError
from dbus.mainloop.glib import DBusGMainLoop


class Manager(PropertiesBase):
    __gsignals__ = {
        str('adapter-added'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
        str('adapter-removed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,))
    }

    @raise_dbus_error
    def __init__(self):
        DBusGMainLoop(set_as_default=True)

        super(Manager, self).__init__('org.freedesktop.DBus.ObjectManager', '/')
        self._handle_signal(self._on_interfaces_added, 'InterfacesAdded')
            self._handle_signal(self._on_interfaces_removed, 'InterfacesRemoved')

    def _on_adapter_added(self, adapter_path):
        dprint(adapter_path)
        self.emit('adapter-added', adapter_path)

    def _on_adapter_removed(self, adapter_path):
        dprint(adapter_path)
        self.emit('adapter-removed', adapter_path)

    def _on_interfaces_added(self, object_path, interfaces):
        if 'org.bluez.Adapter1' in interfaces:
            self.emit('adapter-added', object_path)

    def _on_interfaces_removed(self, object_path, interfaces):
        if 'org.bluez.Adapter1' in interfaces:
            self.emit('adapter-removed', object_path)

    @raise_dbus_error
    def list_adapters(self):
        objects = self._interface.GetManagedObjects()
        adapters = []
        for path, interfaces in objects.items():
            if 'org.bluez.Adapter1' in interfaces:
                adapters.append(path)
        return [Adapter(adapter) for adapter in adapters]

    @raise_dbus_error
    def get_adapter(self, pattern=None):
        adapters = self.list_adapters()
        if pattern is None:
            if len(adapters):
                return adapters[0]
        else:
            for adapter in adapters:
                path = adapter.get_object_path()
                if path == pattern or path == '/org/bluez/'+pattern or adapter.get_properties()['Address'] == pattern:
                    return adapter

        # If the given - or any - adapter does not exist, raise the NoSuchAdapter
        # error BlueZ 4's DefaultAdapter and FindAdapter methods trigger
        raise DBusNoSuchAdapterError('No such adapter')
