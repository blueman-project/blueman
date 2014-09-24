from gi.repository import Gtk
from blueman.Constants import *
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.AppletService import AppletService
from blueman.main.Config import Config
from blueman.Functions import dprint


class Transfer(ServicePlugin):
    __plugin_info__ = (_("Transfer"), "gtk-open")

    def on_load(self, container):

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        self.Builder.add_from_file(UI_PATH + "/services-transfer.ui")
        self.widget = self.Builder.get_object("transfer")

        self.ignored_keys = []

        container.pack_start(self.widget, True, True, 0)
        a = AppletService()
        if "TransferService" in a.QueryPlugins():
            self.setup_transfer()
        else:
            self.widget.props.sensitive = False
            self.widget.props.tooltip_text = _("Applet's transfer service plugin is disabled")

        return True

    def on_enter(self):
        self.widget.props.visible = True

    def on_leave(self):
        self.widget.props.visible = False

    def on_property_changed(self, config, key, value):

        if key == "opp-enabled":
            self.Builder.get_object(key).props.active = value
        if key == "ftp-enabled":
            self.Builder.get_object(key).props.active = value
        if key == "ftp-allow-write":
            self.Builder.get_object(key).props.active = value
        if key == "shared-path":
            self.Builder.get_object(key).set_current_folder(value)
        if key == "browse-command":
            return
        if key == "shared-path":
            self.option_changed_notify(key, False)
        else:
            self.option_changed_notify(key)

    def on_apply(self):
        if self.on_query_apply_state():

            try:
                a = AppletService()
            except:
                dprint("failed to connect to applet")
            else:
                c = self.get_options()
                if "opp-enabled" in c:
                    if not self.TransConf.props.opp-enabled:
                        a.TransferControl("opp", "destroy")

                if "ftp-enabled" in c:
                    if not self.TransConf.props.ftp-enabled:
                        a.TransferControl("ftp", "destroy")

                if "opp-accept" in c or "shared-path" in c or "opp-enabled" in c:
                    if self.TransConf.props.opp-enabled:
                        state = a.TransferStatus("opp")
                        if state == 0:  # destroyed
                            a.TransferControl("opp", "create")
                        elif state == 2:  # running
                            a.TransferControl("opp", "stop")
                            a.TransferControl("opp", "start")
                        elif state == 1:
                            a.TransferControl("opp", "start")

                if "ftp-allow-write" in c or "shared-path" in c or "ftp-enabled" in c:
                    if self.TransConf.props.ftp-enabled:
                        state = a.TransferStatus("ftp")
                        if state == 0:  # destroyed
                            a.TransferControl("ftp", "create")
                        elif state == 2:  # running
                            a.TransferControl("ftp", "stop")
                            a.TransferControl("ftp", "start")
                        elif state == 1:
                            a.TransferControl("ftp", "start")

                self.clear_options()

            dprint("transfer apply")

    def on_query_apply_state(self):
        opts = self.get_options()
        if not opts:
            return False
        else:
            return True

    def setup_transfer(self):
        self.TransConf = Config("transfer")
        self.TransConf.connect("property-changed", self.on_property_changed)
        opp-enabled = self.Builder.get_object("opp-enabled")
        ftp-enabled = self.Builder.get_object("ftp-enabled")
        ftp-allow-write = self.Builder.get_object("ftp-allow-write")
        opp-accept = self.Builder.get_object("opp-accept")
        shared-path = self.Builder.get_object("shared-path")
        obex_cmd = self.Builder.get_object("e_obex_cmd")

        opp-enabled.props.active = self.TransConf.props.opp-enabled
        ftp-enabled.props.active = self.TransConf.props.ftp-enabled
        ftp-allow-write.props.active = self.TransConf.props.ftp-allow-write
        opp-accept.props.active = self.TransConf.props.opp-accept
        if self.TransConf.props.browse-command:
            obex_cmd.props.text = self.TransConf.props.browse-command

        if self.TransConf.props.shared-path is not None:
            shared-path.set_current_folder(self.TransConf.props.shared-path)

        obex_cmd.connect("changed", lambda x: setattr(self.TransConf.props, "browse-command", x.props.text))
        opp-enabled.connect("toggled", lambda x: setattr(self.TransConf.props, "opp-enabled", x.props.active))
        ftp-enabled.connect("toggled", lambda x: setattr(self.TransConf.props, "ftp-enabled", x.props.active))
        ftp-allow-write.connect("toggled", lambda x: setattr(self.TransConf.props, "ftp-allow-write", x.props.active))
        opp-accept.connect("toggled", lambda x: setattr(self.TransConf.props, "opp-accept", x.props.active))
        shared-path.connect("current-folder-changed",
                            lambda x: setattr(self.TransConf.props, "shared-path", x.get_filename()))
