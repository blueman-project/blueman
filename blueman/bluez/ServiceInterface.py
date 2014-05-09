from PropertiesBlueZInterface import PropertiesBlueZInterface
from errors import raise_dbus_error


class ServiceInterface(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, interface, obj_path, methods):
        self.methods = methods
        super(ServiceInterface, self).__init__(interface, obj_path)

    def __getattribute__(self, name):
        if name in object.__getattribute__(self, 'methods'):
            func = getattr(self.get_interface(), name)
            return raise_dbus_error(func)
        else:
            return super(ServiceInterface, self).__getattribute__(name)