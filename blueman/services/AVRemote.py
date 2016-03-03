# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Service import Service
from blueman.Sdp import AV_REMOTE_TARGET_SVCLASS_ID


class AudioSink(Service):
    __group__ = 'audio'
    __svclass_id__ = AV_REMOTE_TARGET_SVCLASS_ID
    __description__ = _("Allows to control media player device")
    __icon__ = "multimedia-player"
    __priority__ = 90
