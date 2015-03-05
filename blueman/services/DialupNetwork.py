from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.services.meta import SerialService
from blueman.Sdp import DIALUP_NET_SVCLASS_ID


class DialupNetwork(SerialService):
    __group__ = 'serial'
    __svclass_id__ = DIALUP_NET_SVCLASS_ID
    __icon__ = "modem"
    __priority__ = 50
