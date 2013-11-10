from BlueZInterface import BlueZInterface
from errors import raise_dbus_error
import types
import dbus


class PropertiesBlueZInterface(BlueZInterface):
    def __init__(self, interface, obj_path):
        super(PropertiesBlueZInterface, self).__init__(interface, obj_path)
        if self.__class__.get_interface_version()[0] >= 5:
            self.__properties_interface = dbus.Interface(self.get_dbus_proxy(), 'org.freedesktop.DBus.Properties')

    @raise_dbus_error
    def set(self, name, value):
        if type(value) is types.IntType:
            value = dbus.UInt32(value)
        if self.__class__.get_interface_version()[0] < 5:
            self.get_interface().SetProperty(name, value)
        else:
            return self.__properties_interface.Set(name, value)

    @raise_dbus_error
    def get_properties(self):
        if self.__class__.get_interface_version()[0] < 5:
            return self.get_interface().GetProperties()
        else:
            return self.__properties_interface.GetAll(self.get_interface_name())

    def _handle_signal(self, handler, signal, interface, obj_path, **kwargs):
        self.get_bus().add_signal_receiver(handler, signal, interface, 'org.bluez', obj_path, **kwargs)

    def handle_signal(self, handler, signal, **kwargs):
        if signal == 'PropertyChanged':
            if self.__class__.get_interface_version()[0] < 5:
                self._handle_signal(
                    handler, 'PropertyChanged', self.get_interface_name(), self.get_object_path(), **kwargs
                )
            else:
                def wrapper(interface_name, changed_properties, invalidated_properties):
                    if interface_name == self.get_interface_name():
                        for name, value in changed_properties.items():
                            handler(name, value)

                interface = 'org.freedesktop.DBus.Properties'

                self._handle_signal(wrapper, 'PropertiesChanged', interface, self.get_object_path(), **kwargs)
        else:
            raise Exception('Unknown signal: %s' % signal)