from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase


class NetworkServer(PropertiesBase):
    def __init__(self, obj_path):
        super(NetworkServer, self).__init__('org.bluez.NetworkServer1', obj_path)

    def register(self, uuid, bridge):
        self._call('Register', uuid, bridge)

    def unregister(self, uuid):
        self._call('Unregister', uuid)
