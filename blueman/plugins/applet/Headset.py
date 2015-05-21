from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.main.Config import Config
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Headset import Headset as BluezHeadset
import dbus


class Headset(AppletPlugin):
    __author__ = "Walmis"
    __description__ = _("Runs a command when answer button is pressed on a headset")
    __icon__ = "blueman-headset"

    __gsettings__ = {
        "schema": "org.blueman.plugins.headset",
        "path": None
    }
    __options__ = {
        "command": {
            "type": str,
            "default": "",
            "name": _("Command"),
            "desc": _("Command to execute when answer button is pressed:")
        }
    }

    _any_headset = None

    def on_load(self, applet):
        self._any_headset = BluezHeadset()
        self._any_headset.connect_signal('answer-requested', self._on_answer_requested)

    def on_unload(self):
        del self._any_headset

    def _on_answer_requested(self, _headset):
        c = self.get_option("command")
        if c and c != "":
            args = c.split(" ")
            launch(args, None, True)
