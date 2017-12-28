from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Adapter import Adapter
from blueman.Sdp import uuid128_to_uuid16
from _blueman import rfcomm_list, create_rfcomm_device, get_rfcomm_channel, RFCOMMError
from blueman.Service import Service
from blueman.main.Mechanism import Mechanism


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
        short_uuid = uuid128_to_uuid16(self.uuid)
        channel = get_rfcomm_channel(short_uuid, props['Address'])
        if channel == 0:
            error = RFCOMMError("Failed to get rfcomm channel")
            if error_handler:
                error_handler(error)
                return True
            else:
                raise error

        try:
            port_id = create_rfcomm_device(Adapter(props['Adapter']).get_properties()['Address'], props['Address'], channel)
            Mechanism().open_rfcomm(port_id)

            if reply_handler:
                reply_handler('/dev/rfcomm%d' % port_id)
        except RFCOMMError as e:
            if error_handler:
                error_handler(e)
            else:
                raise e
        return True

    def disconnect(self, *args):
        Mechanism().close_rfcomm(args[0])
