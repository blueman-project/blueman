from gettext import gettext as _
import logging

from blueman.main.Builder import Builder
from blueman.plugins.ServicePlugin import ServicePlugin
from blueman.main.DBusProxies import AppletService
from blueman.main.Config import Config

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class Transfer(ServicePlugin):
    __plugin_info__ = (_("Transfer"), "document-open")

    def on_load(self, container: Gtk.Box) -> None:

        self._builder = Builder("services-transfer.ui")
        self.widget = self._builder.get_widget("transfer", Gtk.Widget)

        container.pack_start(self.widget, True, True, 0)
        a = AppletService()
        if "TransferService" in a.QueryPlugins():
            self._setup_transfer()
        else:
            self.widget.props.sensitive = False
            self.widget.props.tooltip_text = _("Applet's transfer service plugin is disabled")

    def on_enter(self) -> None:
        self.widget.props.visible = True

    def on_leave(self) -> None:
        self.widget.props.visible = False

    def on_property_changed(self, config: Gio.Settings, key: str) -> None:
        value = config[key]

        if key == "shared-path":
            self._builder.get_widget(key, Gtk.FileChooserButton).set_current_folder(value)
            self.option_changed_notify(key, False)

    def on_apply(self) -> None:
        if self.on_query_apply_state():
            for opt in self.get_options():
                if opt == "shared-path":
                    shared_path = self._builder.get_widget("shared-path", Gtk.FileChooserButton)
                    self._config["shared-path"] = shared_path.get_filename()
                elif opt == "opp-accept":
                    opp_accept = self._builder.get_widget("opp-accept", Gtk.CheckButton)
                    self._config["opp-accept"] = opp_accept.get_active()
                else:
                    raise NotImplementedError("Unknow option: %s" % opt)

            self.clear_options()
            logging.info("transfer apply")

    def on_query_apply_state(self) -> bool:
        opts = self.get_options()
        if not opts:
            return False
        else:
            return True

    def _setup_transfer(self) -> None:
        self._config = Config("org.blueman.transfer")
        self._config.connect("changed", self.on_property_changed)

        opp_accept = self._builder.get_widget("opp-accept", Gtk.CheckButton)
        shared_path = self._builder.get_widget("shared-path", Gtk.FileChooserButton)

        opp_accept.props.active = self._config["opp-accept"]
        if self._config["shared-path"]:
            shared_path.set_current_folder(self._config["shared-path"])

        opp_accept.connect("toggled", lambda x: self.option_changed_notify("opp-accept"))
        shared_path.connect("file-set", lambda x: self.option_changed_notify("shared-path"))
