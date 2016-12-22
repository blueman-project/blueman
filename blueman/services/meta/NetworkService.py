# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from blueman.bluez.errors import BluezDBusException
from blueman.Service import Service
from blueman.bluez.Network import Network


class NetworkService(Service):
    def __init__(self, device, uuid):
        super(NetworkService, self).__init__(device, uuid)
        self._service = Network(device.get_object_path())

    @property
    def connected(self):
        try:
            return self._service['Connected']
        except BluezDBusException:
            logging.warning('Could not get properties of network service', exc_info=True)
            return False

    def connect(self, reply_handler=None, error_handler=None):
        self._service.connect(self.uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None, *args):
        self._service.disconnect(reply_handler=reply_handler, error_handler=error_handler)
