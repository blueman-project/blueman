from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Service import Service
from blueman.Sdp import HEADSET_SVCLASS_ID


class Headset(Service):
    __group__ = 'audio'
    __svclass_id__ = HEADSET_SVCLASS_ID
    __icon__ = "blueman-handsfree"
    __priority__ = 10
