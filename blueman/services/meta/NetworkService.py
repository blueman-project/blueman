from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from dbus import DBusException
from blueman.Service import Service
from blueman.bluez.Network import Network


class NetworkService(Service):
    def __init__(self, device, uuid):
        super(NetworkService, self).__init__(device, uuid, False)
        self._service = Network(device.get_object_path())

    @property
    def connected(self):
        try:
            return self._service.get_properties()['Connected']
        except DBusException as e:
            dprint('Could not get properties of network service: %s' % e)
            return False

    def connect(self, reply_handler=None, error_handler=None):
        self._service.connect(self.uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None, *args):
        self._service.disconnect(reply_handler=reply_handler, error_handler=error_handler)
