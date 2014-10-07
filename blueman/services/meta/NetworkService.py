from blueman.Service import Service
from blueman.bluez.Network import Network


class NetworkService(Service):
    def __init__(self, device, uuid):
        super(NetworkService, self).__init__(device, uuid, False)
        self._service = Network(device.get_object_path())

    @property
    def connected(self):
        return self._service.get_properties()['Connected']

    def connect(self, reply_handler=None, error_handler=None):
        self._service.connect(self.uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None, *args):
        # TODO: TypeError: disconnect() got multiple values for keyword argument 'reply_handler'
        self._service.disconnect(self.uuid, reply_handler=reply_handler, error_handler=error_handler)
