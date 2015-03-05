from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.services.meta import SerialService
from blueman.Sdp import SERIAL_PORT_SVCLASS_ID


class SerialPort(SerialService):
    __group__ = 'serial'
    __svclass_id__ = SERIAL_PORT_SVCLASS_ID
    __icon__ = "blueman-serial"
    __priority__ = 50
