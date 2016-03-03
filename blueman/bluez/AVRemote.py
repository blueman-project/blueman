# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase
from gi.repository import GObject


class AVRemote(PropertiesBase):
    __gsignals__ = {
        str('status-changed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,))
    }

    _interface_name = 'org.bluez.MediaPlayer1'

    def _init(self, obj_path):
        super(AVRemote, self)._init(self._interface_name, obj_path)

    def play(self):
        self._call('Play')

    def pause(self):
        self._call('Pause')

    def stop(self):
        self._call('Stop')

    def next(self):
        self._call('Next')

    def previous(self):
        self._call('Previous')

    def fast_forward(self):
        self._call('FastForward')

    def rewind(self):
        self._call('Rewind')
