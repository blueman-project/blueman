from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.Config import Config
from blueman.Functions import *
from blueman.Constants import *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class GsmSettings(Gtk.Dialog):
    def __init__(self, bd_address):
        GObject.GObject.__init__(self)

        self.device = bd_address

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        self.Builder.add_from_file(UI_PATH + "/gsm-settings.ui")

        vbox = self.Builder.get_object("vbox1")

        self.config = Config("org.blueman.gsmsetting", "/org/blueman/gsmsettings/%s/" % bd_address)
        self.props.icon_name = "network-wireless"
        self.props.title = _("GSM Settings")

        self.props.resizable = False

        a = self.get_content_area()
        a.pack_start(vbox, True, True, 0)
        vbox.show()

        self.e_apn = self.Builder.get_object("e_apn")
        self.e_number = self.Builder.get_object("e_number")

        self.config.bind_to_widget("apn", self.e_apn, "text")
        self.config.bind_to_widget("number", self.e_number, "text")

        self.add_button("_Close", Gtk.ResponseType.CLOSE)
