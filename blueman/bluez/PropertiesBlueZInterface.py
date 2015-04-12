from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.BlueZInterface import BlueZInterface
from blueman.bluez.errors import raise_dbus_error
import dbus


class PropertiesBlueZInterface(BlueZInterface):
    def __init__(self, interface, obj_path):
        super(PropertiesBlueZInterface, self).__init__(interface, obj_path)

        self._handler_wrappers = {}

        if self.__class__.get_interface_version()[0] >= 5 and obj_path:
            self.__properties_interface = dbus.Interface(self.get_dbus_proxy(), 'org.freedesktop.DBus.Properties')

    @raise_dbus_error
    def set(self, name, value):
        if type(value) is int:
            value = dbus.UInt32(value)
        if self.__class__.get_interface_version()[0] < 5:
            self.get_interface().SetProperty(name, value)
        else:
            return self.__properties_interface.Set(self.get_interface_name(), name, value)

    @raise_dbus_error
    def get_properties(self):
        if self.__class__.get_interface_version()[0] < 5:
            return self.get_interface().GetProperties()
        else:
            return self.__properties_interface.GetAll(self.get_interface_name())

    def _handle_signal(self, handler, signal, interface, obj_path, **kwargs):
        self.get_bus().add_signal_receiver(handler, signal, interface, 'org.bluez', obj_path, **kwargs)

    def _unhandle_signal(self, handler, signal, interface, obj_path, **kwargs):
        self.get_bus().remove_signal_receiver(
            handler, signal, self.get_interface_name(), 'org.bluez',
            self.get_object_path(), **kwargs
        )

    def handle_signal(self, handler, signal, **kwargs):
        if signal == 'PropertyChanged':
            if self.__class__.get_interface_version()[0] < 5:
                self._handle_signal(
                    handler, 'PropertyChanged', self.get_interface_name(), self.get_object_path(), **kwargs
                )
            else:
                def wrapper(interface_name, changed_properties, invalidated_properties, **kwargs):
                    if interface_name == self.get_interface_name():
                        for name, value in changed_properties.items():
                            handler(name, value, **kwargs)

                self._handler_wrappers[handler] = wrapper

                interface = 'org.freedesktop.DBus.Properties'

                self._handle_signal(wrapper, 'PropertiesChanged', interface, self.get_object_path(), **kwargs)
        else:
            raise Exception('Unknown signal: %s' % signal)

    def unhandle_signal(self, handler, signal, **kwargs):
        if signal == 'PropertyChanged':
            if self.__class__.get_interface_version()[0] < 5:
                self._unhandle_signal(handler, signal, self.get_interface_name(), self.get_object_path(), **kwargs)
            else:
                self._unhandle_signal(self._handler_wrappers[handler], 'PropertiesChanged',
                                      'org.freedesktop.DBus.Properties', self.get_object_path(), **kwargs)
        else:
            raise Exception('Unknown signal: %s' % signal)
