# coding=utf-8
from blueman.services.meta import SerialService
from blueman.Sdp import SERIAL_PORT_SVCLASS_ID


class SerialPort(SerialService):
    __group__ = 'serial'
    __svclass_id__ = SERIAL_PORT_SVCLASS_ID
    __icon__ = "blueman-serial"
    __priority__ = 50
