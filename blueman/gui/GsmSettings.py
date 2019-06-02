# coding=utf-8
from locale import bind_textdomain_codeset

from blueman.main.Config import Config
from blueman.Constants import *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class GsmSettings(Gtk.Dialog):
    def __init__(self, bd_address):
        super().__init__()

        self.set_name("GsmSettings")
        self.device = bd_address

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
        self.Builder.add_from_file(UI_PATH + "/gsm-settings.ui")

        gsm_grid = self.Builder.get_object("gsm_grid")

        self.config = Config("org.blueman.gsmsetting", "/org/blueman/gsmsettings/%s/" % bd_address)
        self.props.icon_name = "network-wireless"
        self.props.title = _("GSM Settings")

        self.props.resizable = False

        a = self.get_content_area()
        a.pack_start(gsm_grid, True, True, 0)
        gsm_grid.show()

        self.e_apn = self.Builder.get_object("e_apn")
        self.e_number = self.Builder.get_object("e_number")

        self.config.bind_to_widget("apn", self.e_apn, "text")
        self.config.bind_to_widget("number", self.e_number, "text")

        self.add_button("_Close", Gtk.ResponseType.CLOSE)
