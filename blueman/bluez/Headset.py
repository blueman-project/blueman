from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.errors import raise_dbus_error


class Headset(PropertiesBase):
    __gsignals__ = {str('answer-requested'): (GObject.SignalFlags.NO_HOOKS, None, ())}

    @raise_dbus_error
    def __init__(self, obj_path=None):
        super(Headset, self).__init__('org.bluez.Headset1', obj_path)
        self._handle_signal(self._on_answer_requested, 'AnswerRequested')

    def _on_answer_requested(self):
        self.emit('answer-requested')
