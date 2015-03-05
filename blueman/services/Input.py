from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Service import Service
from blueman.Sdp import HID_SVCLASS_ID


class Input(Service):
    __svclass_id__ = HID_SVCLASS_ID
    __icon__ = "mouse"
    __priority__ = 1
