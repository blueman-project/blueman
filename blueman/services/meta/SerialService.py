from blueman.bluez.Adapter import Adapter
from blueman.Lib import rfcomm_list, release_rfcomm_device, create_rfcomm_device
from blueman.Service import Service


class SerialService(Service):
    def __init__(self, device, uuid):
        super(SerialService, self).__init__(device, uuid, False)

    def serial_port_id(self, channel):
        for dev in rfcomm_list():
            if dev["dst"] == self.device.Address and dev["state"] == "connected" and dev["channel"] == channel:
                return dev["id"]

    @property
    def connected(self):
        return False

    def connect(self, reply_handler=None, error_handler=None):
        props = self.device.get_properties()
        try:
            # TODO: Channel?
            port_id = create_rfcomm_device(Adapter(props['Adapter']).get_properties()['Address'], props['Address'], 1)
            if reply_handler:
                reply_handler('/dev/rfcomm%d' % port_id)
        except Exception as e:
            if error_handler:
                error_handler(e)
            else:
                raise e
        return True

    def disconnect(self, *args):
        release_rfcomm_device(args[0])
