from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBlueZInterface import PropertiesBlueZInterface
from blueman.bluez.errors import raise_dbus_error


class NetworkServer(PropertiesBlueZInterface):
    @raise_dbus_error
    def __init__(self, obj_path):
        super(NetworkServer, self).__init__('org.bluez.NetworkServer1', obj_path)

    @raise_dbus_error
    def register(self, uuid, bridge):
        self.get_interface().Register(uuid, bridge)

    @raise_dbus_error
    def unregister(self, uuid):
        self.get_interface().Unregister(uuid)
