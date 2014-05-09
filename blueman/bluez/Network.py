from PropertiesBlueZInterface import PropertiesBlueZInterface
from errors import raise_dbus_error


class Network(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.Network'
        else:
            interface = 'org.bluez.Network1'

        super(Network, self).__init__(interface, obj_path)
