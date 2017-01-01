# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Adapter import Adapter
from _blueman import rfcomm_list, release_rfcomm_device, create_rfcomm_device
from blueman.Service import Service
from blueman.main.Mechanism import Mechanism


class SerialService(Service):
    def __init__(self, device, uuid):
        super(SerialService, self).__init__(device, uuid)

    def serial_port_id(self, channel):
        for dev in rfcomm_list():
            if dev["dst"] == self.device['Address'] and dev["state"] == "connected" and dev["channel"] == channel:
                return dev["id"]

    @property
    def connected(self):
        return False

    def connect(self, reply_handler=None, error_handler=None):
        try:
            # TODO: Channel?
            port_id = create_rfcomm_device(Adapter(self.device["Adapter"])['Address'], self.device["Address"], 1)
            Mechanism().open_rfcomm(str('(d)'), port_id)
            if reply_handler:
                reply_handler('/dev/rfcomm%d' % port_id)
        except Exception as e:
            if error_handler:
                error_handler(e)
            else:
                raise e
        return True

    def disconnect(self, *args):
        Mechanism().close_rfcomm(str('(d)'), args[0])
        release_rfcomm_device(args[0])
