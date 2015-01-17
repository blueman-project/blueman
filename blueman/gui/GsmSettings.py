from blueman.main.Config import Config
from blueman.Functions import *
from blueman.Constants import *

from gi.repository import Gtk


class GsmSettings(Gtk.Dialog):
    def __init__(self, bd_address):
        GObject.GObject.__init__(self)

        self.device = bd_address

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        self.Builder.add_from_file(UI_PATH + "/gsm-settings.ui")

        vbox = self.Builder.get_object("vbox1")

        self.config = Config("gsm_settings/" + bd_address)
        self.props.icon_name = "network-wireless"
        self.props.title = _("GSM Settings")

        self.props.resizable = False

        a = self.get_content_area()
        a.pack_start(vbox, True, True, 0)
        vbox.show()

        self.e_apn = self.Builder.get_object("e_apn")
        self.e_number = self.Builder.get_object("e_number")

        if self.config.props.apn == None:
            self.config.props.apn = ""

        if self.config.props.number == None:
            self.config.props.number = "*99#"

        self.e_apn.props.text = self.config.props.apn
        self.e_number.props.text = self.config.props.number

        self.e_apn.connect("changed", self.on_changed)
        self.e_number.connect("changed", self.on_changed)

        self.add_button("_Close", Gtk.ResponseType.CLOSE)

    def on_changed(self, e):
        if e == self.e_apn:
            self.config.props.apn = e.props.text
        elif e == self.e_number:
            self.config.props.number = e.props.text
