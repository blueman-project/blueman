from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.services.meta import SerialService
from blueman.Sdp import DIALUP_NET_SVCLASS_ID
from blueman.main.Mechanism import Mechanism


class DialupNetwork(SerialService):
    __group__ = 'serial'
    __svclass_id__ = DIALUP_NET_SVCLASS_ID
    __icon__ = "modem"
    __priority__ = 50

    def disconnect(self, port):
        Mechanism().PPPDisconnect(port)
        super().disconnect(port)
