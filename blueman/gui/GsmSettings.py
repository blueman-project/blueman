from gettext import gettext as _

from blueman.main.Builder import Builder

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gio


class GsmSettings(Gtk.Dialog):
    def __init__(self, bd_address: str) -> None:
        super().__init__()

        self.set_name("GsmSettings")
        self.device = bd_address

        builder = Builder("gsm-settings.ui")

        gsm_grid = builder.get_widget("gsm_grid", Gtk.Grid)

        self.config = Gio.Settings(schema_id="org.blueman.gsmsetting",
                                   path=f"/org/blueman/gsmsettings/{bd_address}/")
        self.props.icon_name = "network-wireless-symbolic"
        self.props.title = _("GSM Settings")

        self.props.resizable = False

        a = self.get_content_area()
        a.pack_start(gsm_grid, True, True, 0)
        gsm_grid.show()

        self.e_apn = builder.get_widget("e_apn", Gtk.Entry)
        self.e_number = builder.get_widget("e_number", Gtk.Entry)

        self.config.bind("apn", self.e_apn, "text", Gio.SettingsBindFlags.DEFAULT)
        self.config.bind("number", self.e_number, "text", Gio.SettingsBindFlags.DEFAULT)

        self.add_button(_("_Close"), Gtk.ResponseType.CLOSE)
