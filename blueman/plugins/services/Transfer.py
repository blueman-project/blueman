# coding=utf-8
from locale import bind_textdomain_codeset
import logging

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blueman.Constants import *
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.AppletService import AppletService
from blueman.main.Config import Config


class Transfer(ServicePlugin):
    __plugin_info__ = (_("Transfer"), "document-open")

    def on_load(self, container):

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
        self.Builder.add_from_file(UI_PATH + "/services-transfer.ui")
        self.widget = self.Builder.get_object("transfer")

        self.ignored_keys = []

        container.pack_start(self.widget, True, True, 0)
        a = AppletService()
        if "TransferService" in a.QueryPlugins():
            self._setup_transfer()
        else:
            self.widget.props.sensitive = False
            self.widget.props.tooltip_text = _("Applet's transfer service plugin is disabled")

        return True

    def on_enter(self):
        self.widget.props.visible = True

    def on_leave(self):
        self.widget.props.visible = False

    def on_property_changed(self, config, key):
        value = config[key]

        if key == "shared-path":
            self.Builder.get_object(key).set_current_folder(value)
            self.option_changed_notify(key, False)

    def on_apply(self):
        if self.on_query_apply_state():
            self.clear_options()
            logging.info("transfer apply")

    def on_query_apply_state(self):
        opts = self.get_options()
        if not opts:
            return False
        else:
            return True

    def _setup_transfer(self):
        self._config = Config("org.blueman.transfer")
        self._config.connect("changed", self.on_property_changed)

        opp_accept = self.Builder.get_object("opp-accept")
        shared_path = self.Builder.get_object("shared-path")

        opp_accept.props.active = self._config["opp-accept"]
        if self._config["shared-path"]:
            shared_path.set_current_folder(self._config["shared-path"])

        opp_accept.connect("toggled", lambda x: self._config.set_boolean("opp-accept", x.props.active))

        shared_path.connect("file-set", lambda x: self._config.set_string("shared-path", x.get_filename()))
