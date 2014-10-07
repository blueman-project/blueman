from blueman.Service import Service
from blueman.Sdp import HID_SVCLASS_ID


class Input(Service):
    __svclass_id__ = HID_SVCLASS_ID
    __icon__ = "mouse"
    __priority__ = 1
