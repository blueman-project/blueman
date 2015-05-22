from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error


class NetworkServer(PropertiesBase):
    @raise_dbus_error
    def __init__(self, obj_path):
        super(NetworkServer, self).__init__('org.bluez.NetworkServer1', obj_path)

    @raise_dbus_error
    def register(self, uuid, bridge):
        self._interface.Register(uuid, bridge)

    @raise_dbus_error
    def unregister(self, uuid):
        self._interface.Unregister(uuid)
