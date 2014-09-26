from gi.repository import Gtk, Gio
from blueman.Constants import *
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.AppletService import AppletService
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
                    if not self.Settings["opp-enabled"]:
                        a.TransferControl("opp", "destroy")

                if "ftp-enabled" in c:
                    if not self.Settings["ftp-enabled"]:
                        a.TransferControl("ftp", "destroy")

                if "opp-accept" in c or "shared-path" in c or "opp-enabled" in c:
                    if self.Settings["opp-enabled"]:
                        state = a.TransferStatus("opp")
                        if state == 0:  # destroyed
                            a.TransferControl("opp", "create")
                        elif state == 2:  # running
                            a.TransferControl("opp", "stop")
                            a.TransferControl("opp", "start")
                        elif state == 1:
                            a.TransferControl("opp", "start")

                if "ftp-allow-write" in c or "shared-path" in c or "ftp-enabled" in c:
                    if self.Settings["ftp-enabled"]:
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
        self.Settings = Gio.Settings.new(BLUEMAN_TRANSFER_GSCHEMA)
        self.Settings.connect("changed", self.on_property_changed)
        opp_enabled = self.Builder.get_object("opp-enabled")
        ftp_enabled = self.Builder.get_object("ftp-enabled")
        ftp_allow_write = self.Builder.get_object("ftp-allow-write")
        opp_accept = self.Builder.get_object("opp-accept")
        shared_path = self.Builder.get_object("shared-path")
        obex_cmd = self.Builder.get_object("e_obex_cmd")

        opp_enabled.props.active = self.Settings["opp-enabled"]
        ftp_enabled.props.active = self.Settings["ftp-enabled"]
        ftp_allow_write.props.active = self.Settings["ftp-allow-write"]
        opp_accept.props.active = self.Settings["opp-accept"]
        if self.Settings["browse-command"]:
            obex_cmd.props.text = self.Settings["browse-command"]

        if not self.Settings["shared-path"]:
            shared-path.set_current_folder(self.Settings["shared-path"])

        obex_cmd.connect("changed", lambda x: setattr(self.Settings, "browse-command", x.props.text))
        opp_enabled.connect("toggled", lambda x: setattr(self.Settings, "opp-enabled", x.props.active))
        ftp_enabled.connect("toggled", lambda x: setattr(self.Settings, "ftp-enabled", x.props.active))
        ftp_allow_write.connect("toggled", lambda x: setattr(self.Settings, "ftp-allow-write", x.props.active))
        opp_accept.connect("toggled", lambda x: setattr(self.Settings, "opp-accept", x.props.active))
        shared_path.connect("current-folder-changed",
                            lambda x: setattr(self.Settings, "shared-path", x.get_filename()))
