from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase


class Network(PropertiesBase):
    def __init__(self, obj_path=None):
        super(Network, self).__init__('org.bluez.Network1', obj_path)

    def connect(self, uuid, reply_handler=None, error_handler=None):
        self._call('Connect', uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None):
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)
