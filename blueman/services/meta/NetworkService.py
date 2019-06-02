# coding=utf-8
from blueman.Service import Service
from blueman.bluez.Network import Network


class NetworkService(Service):
    def __init__(self, device, uuid):
        super().__init__(device, uuid)
        self._service = Network(device.get_object_path())

    @property
    def available(self):
        # This interface is only available after pairing
        return self.device["Paired"]

    @property
    def connected(self):
        if not self.available:
            return False

        return self._service['Connected']

    def connect(self, reply_handler=None, error_handler=None):
        self._service.connect(self.uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None, *args):
        self._service.disconnect(reply_handler=reply_handler, error_handler=error_handler)
