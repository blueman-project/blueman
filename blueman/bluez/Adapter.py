from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error
from blueman.bluez.Device import Device
import dbus


class Adapter(PropertiesBase):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        interface = 'org.bluez.Adapter1'
        proxy = dbus.SystemBus().get_object('org.bluez', '/', follow_name_owner_changes=True)
        self.manager_interface = dbus.Interface(proxy, 'org.freedesktop.DBus.ObjectManager')

        super(Adapter, self).__init__(interface, obj_path)

    @raise_dbus_error
    def find_device(self, address):
        devices = self.list_devices()
        for device in devices:
            if device.get_properties()['Address'] == address:
                return device

    @raise_dbus_error
    def list_devices(self):
        objects = self.manager_interface.GetManagedObjects()
        devices = []
        for path, interfaces in objects.items():
            if 'org.bluez.Device1' in interfaces:
                devices.append(path)
        return [Device(device) for device in devices]

    @raise_dbus_error
    def handle_signal(self, handler, signal, **kwargs):
        if signal in ['DeviceCreated', 'DeviceRemoved']:
            def wrapper(object_path, interfaces):
                if 'org.bluez.Device1' in interfaces:
                    handler(object_path)

            self._handler_wrappers[handler] = wrapper

            signal = {
                'DeviceCreated': 'InterfacesAdded',
                'DeviceRemoved': 'InterfacesRemoved'
            }[signal]

            self._handle_signal(wrapper, signal, 'org.freedesktop.DBus.ObjectManager', '/', **kwargs)
        else:
            super(Adapter, self).handle_signal(handler, signal, **kwargs)

    @raise_dbus_error
    def unhandle_signal(self, handler, signal, **kwargs):
        if signal in ['DeviceCreated', 'DeviceRemoved']:
            signal = {
                'DeviceCreated': 'InterfacesAdded',
                'DeviceRemoved': 'InterfacesRemoved'
            }[signal]

            self._unhandle_signal(self._handler_wrappers[handler], signal, self.get_interface_name(),
                                  self.get_object_path(), **kwargs)
        else:
            super(Adapter, self).unhandle_signal(handler, signal, **kwargs)

    @raise_dbus_error
    def start_discovery(self):
        self.get_interface().StartDiscovery()

    @raise_dbus_error
    def stop_discovery(self):
        self.get_interface().StopDiscovery()

    @raise_dbus_error
    def remove_device(self, device):
        self.get_interface().RemoveDevice(device.get_object_path())

    @raise_dbus_error
    def get_name(self):
        props = self.get_properties()
        try:
            return props['Alias']
        except KeyError:
            return props['Name']

    @raise_dbus_error
    def set_name(self, name):
        try:
            return self.set('Alias', name)
        except dbus.exceptions.DBusException:
            return self.set('Name', name)
