from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Headset import Headset as BluezHeadset
import dbus
from gi.repository import Gio

class Headset(AppletPlugin):
    __author__ = "Walmis"
    __description__ = _("Runs a command when answer button is pressed on a headset")
    __icon__ = "blueman-headset"

    __options__ = {
        "command": {
            "type": str,
            "default": "",
            "name": _("Command"),
            "desc": _("Command to execute when answer button is pressed:")
        }
    }

    def __init__(self):
        self.Settings = Gio.Settings.new(BLUEMAN_HEADSET_GSCHEMA)

    def on_load(self, applet):
        BluezHeadset().handle_signal(self.on_answer_requested, 'AnswerRequested')

    def on_unload(self):
        BluezHeadset().unhandle_signal(self.on_answer_requested, 'AnswerRequested')

    def on_answer_requested(self):
        c = self.Settings["command"]
        if c and c != "":
            args = c.split(" ")
            try:
                spawn(args, True)
            except:
                dprint("Cannot launch command")
