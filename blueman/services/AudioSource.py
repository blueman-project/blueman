from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Service import Service
from blueman.Sdp import AUDIO_SOURCE_SVCLASS_ID


class AudioSource(Service):
    __group__ = 'audio'
    __svclass_id__ = AUDIO_SOURCE_SVCLASS_ID
    __description__ = _("Allows to receive audio from remote device")
    __icon__ = "blueman-headset"
    __priority__ = 21

    @property
    def connected(self):
        if self._legacy_interface:
            return self._legacy_interface.GetProperties()['State'] != 'disconnected'
        else:
            return super(AudioSource, self).connected
