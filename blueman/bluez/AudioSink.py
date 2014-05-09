from PropertiesBlueZInterface import PropertiesBlueZInterface
from errors import raise_dbus_error


class AudioSink(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.AudioSink'
        else:
            interface = 'org.bluez.AudioSink1'

        super(AudioSink, self).__init__(interface, obj_path)
