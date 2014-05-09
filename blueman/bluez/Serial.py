from PropertiesBlueZInterface import PropertiesBlueZInterface
from errors import raise_dbus_error


class Serial(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.Serial'
        else:
            interface = 'org.bluez.Serial1'

        super(Serial, self).__init__(interface, obj_path)
