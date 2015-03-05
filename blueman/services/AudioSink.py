from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Service import Service
from blueman.Sdp import AUDIO_SINK_SVCLASS_ID


class AudioSink(Service):
    __group__ = 'audio'
    __svclass_id__ = AUDIO_SINK_SVCLASS_ID
    __description__ = _("Allows to send audio to remote device")
    __icon__ = "blueman-headset"
    __priority__ = 20
