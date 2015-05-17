from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Adapter import Adapter
from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error, DBusNoSuchAdapterError
from dbus.mainloop.glib import DBusGMainLoop


class Manager(PropertiesBase):
    @raise_dbus_error
    def __init__(self):
        DBusGMainLoop(set_as_default=True)

        super(Manager, self).__init__('org.freedesktop.DBus.ObjectManager', '/')

    @raise_dbus_error
    def list_adapters(self):
        objects = self.get_interface().GetManagedObjects()
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

    def handle_signal(self, handler, signal, **kwargs):
        if signal == 'AdapterAdded' or signal == 'AdapterRemoved':
            def wrapper(object_path, interfaces):
                if 'org.bluez.Adapter1' in interfaces:
                    handler(object_path)

            self._handler_wrappers[handler] = wrapper

            signal = signal.replace('Adapter', 'Interfaces')

            self._handle_signal(wrapper, signal, self.get_interface_name(), self.get_object_path(), **kwargs)
        else:
            super(Manager, self).handle_signal(handler, signal, **kwargs)

    def unhandle_signal(self, handler, signal, **kwargs):
        if signal == 'AdapterAdded' or signal == 'AdapterRemoved':
            handler = self._handler_wrappers[handler]
            signal = signal.replace('Adapter', 'Interfaces')

            self._unhandle_signal(handler, signal, self.get_interface_name(), self.get_object_path(), **kwargs)
        else:
            super(Manager, self).unhandle_signal(handler, signal, **kwargs)
