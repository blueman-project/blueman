from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBlueZInterface import PropertiesBlueZInterface
from blueman.bluez.errors import raise_dbus_error


class Network(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path=None):
        if self.__class__.get_interface_version()[0] < 5:
            interface = 'org.bluez.Network'
        else:
            interface = 'org.bluez.Network1'

        super(Network, self).__init__(interface, obj_path)

    @raise_dbus_error
    def connect(self, uuid, reply_handler=None, error_handler=None):
        self.get_interface().Connect(uuid, reply_handler=reply_handler, error_handler=error_handler)

    @raise_dbus_error
    def disconnect(self, reply_handler=None, error_handler=None):
        self.get_interface().Disconnect(reply_handler=reply_handler, error_handler=error_handler)
