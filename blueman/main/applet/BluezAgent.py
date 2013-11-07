# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
import dbus
import dbus.glib
import dbus.service
import os.path
from blueman.Functions import get_icon, dprint
import gtk
import gobject
import cgi
import blueman.bluez as Bluez
from blueman.Sdp import *
from blueman.Constants import *
from blueman.gui.Notification import Notification

from blueman.bluez.Agent import Agent, AgentMethod


class AgentErrorRejected(dbus.DBusException):
    def __init__(self):
        dbus.DBusException.__init__(self, name="org.bluez.Error.Rejected")


class AgentErrorCanceled(dbus.DBusException):
    def __init__(self):
        dbus.DBusException.__init__(self, name="org.bluez.Error.Canceled")


class DummyGObjectMeta(dbus.service.InterfaceType, gobject.GObjectMeta):
    pass


class CommonAgent(gobject.GObject, Agent):
    __metaclass__ = DummyGObjectMeta
    __gsignals__ = {
    'released': (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
    }

    def __init__(self, status_icon, path):
        Agent.__init__(self, path)
        gobject.GObject.__init__(self)

        self.status_icon = status_icon
        self.dbus_path = path
        self.dialog = None
        self.n = None

    def build_passkey_dialog(self, device_alias, dialog_msg, is_numeric):
        def on_insert_text(editable, new_text, new_text_length, position):
            if not new_text.isdigit():
                editable.stop_emission("insert-text")

        builder = gtk.Builder()
        builder.add_from_file(UI_PATH + "/applet-passkey.ui")
        builder.set_translation_domain("blueman")
        dialog = builder.get_object("dialog")

        dialog.props.icon_name = "blueman"
        dev_name = builder.get_object("device_name")
        dev_name.set_markup(device_alias)
        msg = builder.get_object("message")
        msg.set_text(dialog_msg)
        pin_entry = builder.get_object("pin_entry")
        show_input = builder.get_object("show_input_check")
        if (is_numeric):
            pin_entry.set_max_length(6)
            pin_entry.set_width_chars(6)
            pin_entry.connect("insert-text", on_insert_text)
            show_input.hide()
        else:
            pin_entry.set_max_length(16)
            pin_entry.set_width_chars(16)
            pin_entry.set_visibility(False)
        show_input.connect("toggled", lambda x: pin_entry.set_visibility(x.props.active))
        accept_button = builder.get_object("accept")
        pin_entry.connect("changed", lambda x: accept_button.set_sensitive(x.get_text() != ''))

        return (dialog, pin_entry)

    def get_device_alias(self, device_path):
        device = Bluez.Device(device_path)
        props = device.GetProperties()
        address = props["Address"]
        name = props["Name"]
        alias = address
        if name:
            alias = "<b>%s</b> (%s)" % (cgi.escape(name), address)
        return alias


    def ask_passkey(self, device_path, dialog_msg, notify_msg, is_numeric, notification, ok, err):
        def on_notification_close(n, action):
            if action != "closed":
                self.dialog.present()
            else:
                if self.dialog:
                    self.dialog.response(gtk.RESPONSE_REJECT)
                #self.applet.status_icon.set_blinking(False)


        def passkey_dialog_cb(dialog, response_id):
            if response_id == gtk.RESPONSE_ACCEPT:
                ret = pin_entry.get_text()
                if is_numeric:
                    ret = int(ret)
                ok(ret)
            else:
                err(AgentErrorRejected())
            dialog.destroy()
            self.dialog = None

        alias = self.get_device_alias(device_path)
        notify_message = _("Pairing request for %s") % (alias)

        if self.dialog:
            dprint("Agent: Another dialog still active, cancelling")
            err(AgentErrorCanceled())

        self.dialog, pin_entry = self.build_passkey_dialog(alias, dialog_msg, is_numeric)
        if not self.dialog:
            dprint("Agent: Failed to build dialog")
            err(AgentErrorCanceled())

        if notification:
            Notification(_("Bluetooth Authentication"), notify_message, pixbuf=get_icon("blueman", 48),
                         status_icon=self.status_icon)
        #self.applet.status_icon.set_blinking(True)

        self.dialog.connect("response", passkey_dialog_cb)
        self.dialog.present()

    def __del__(self):
        dprint("Agent on path", self.dbus_path, "deleted")

    @AgentMethod
    def Release(self):
        dprint("Agent.Release")
        self.Cancel()
        self.remove_from_connection()
        self.emit("released")

    @AgentMethod
    def Cancel(self):
        dprint("Agent.Cancel")
        if self.dialog:
            self.dialog.response(gtk.RESPONSE_REJECT)
        try:
            self.n.close()
        except:
            pass


class AdapterAgent(CommonAgent):
    def __init__(self, status_icon, adapter, time_func):
        self.adapter = adapter
        self.n = None
        self.time_func = time_func

        adapter_name = os.path.basename(adapter.GetObjectPath())

        CommonAgent.__init__(self, status_icon, "/org/blueman/agent/adapter/" + adapter_name)

    @AgentMethod
    def RequestPinCode(self, device, ok, err):
        dprint("Agent.RequestPinCode")
        dialog_msg = _("Enter PIN code for authentication:")
        notify_msg = _("Enter PIN code")
        self.ask_passkey(device, dialog_msg, notify_msg, False, True, ok, err)
        if self.dialog:
            self.dialog.present_with_time(self.time_func())

    @AgentMethod
    def RequestPasskey(self, device, ok, err):
        dprint("Agent.RequestPasskey")
        dialog_msg = _("Enter passkey for authentication:")
        notify_msg = _("Enter passkey")
        self.ask_passkey(device, dialog_msg, notify_msg, True, True, ok, err)
        if self.dialog:
            self.dialog.present_with_time(self.time_func())

    @AgentMethod
    def DisplayPasskey(self, device, passkey, entered):
        dprint("Agent.DisplayPasskey")

    @AgentMethod
    def RequestConfirmation(self, device, passkey, ok, err):
        def on_confirm_action(n, action):
            #self.applet.status_icon.set_blinking(False)
            if action == "confirm":
                ok()
            else:
                err(AgentErrorRejected())

        dprint("Agent.RequestConfirmation")
        alias = self.get_device_alias(device)
        notify_message = (_("Pairing request for:") + "\n%s\n" + _(
            "Confirm value for authentication:") + " <b>%s</b>") % (alias, passkey)
        actions = [["confirm", _("Confirm"), "gtk-yes"], ["deny", _("Deny"), "gtk-no"]]

        Notification("Bluetooth", notify_message, 0,
                     actions, on_confirm_action,
                     pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)

    #self.applet.status_icon.set_blinking(True)


    @AgentMethod
    def Authorize(self, device, uuid, ok, err):

        def on_auth_action(n, action):
            dprint(action)

            #self.applet.status_icon.set_blinking(False)
            if action == "always":
                device = Bluez.Device(n._device)
                device.SetProperty("Trusted", True)
            if action == "always" or action == "accept":
                ok()
            else:
                err(AgentErrorRejected())

            self.n = None

        dprint("Agent.Authorize")
        alias = self.get_device_alias(device)
        uuid16 = uuid128_to_uuid16(uuid)
        service = uuid16_to_name(uuid16)
        notify_message = (_("Authorization request for:") + "\n%s\n" + _("Service:") + " <b>%s</b>") % (alias, service)
        actions = [["always", _("Always accept"), "blueman-trust"],
                   ["accept", _("Accept"), "gtk-yes"],
                   ["deny", _("Deny"), "gtk-no"]]

        n = Notification(_("Bluetooth Authentication"), notify_message, 0,
                         actions, on_auth_action,
                         pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)
        n._device = device

    #self.applet.status_icon.set_blinking(True)

    @AgentMethod
    def ConfirmModeChange(self, mode, ok, err):
        dprint("Agent.ConfirmModeChange")


class TempAgent(CommonAgent):
    def __init__(self, status_icon, path, time):
        CommonAgent.__init__(self, status_icon, path)
        self.time = time

    @AgentMethod
    def RequestPinCode(self, device, ok, err):
        dprint("Agent.RequestPinCode")
        dialog_msg = _("Enter PIN code for authentication:")
        notify_msg = _("Enter PIN code")
        self.ask_passkey(device, dialog_msg, notify_msg, False, False, ok, err)
        if self.dialog:
            self.dialog.present_with_time(self.time)

    @AgentMethod
    def RequestPasskey(self, device, ok, err):
        dprint("Agent.RequestPasskey")
        dialog_msg = _("Enter passkey for authentication:")
        notify_msg = _("Enter passkey")
        self.ask_passkey(device, dialog_msg, notify_msg, True, False, ok, err)
        if self.dialog:
            self.dialog.present_with_time(self.time)

    @AgentMethod
    def RequestConfirmation(self, device, passkey, ok, err):
        dprint("Agent.RequestConfirmation")
        alias = self.get_device_alias(device)

        dialog = gtk.MessageDialog(buttons=gtk.BUTTONS_YES_NO)
        dialog.props.use_markup = True
        dialog.props.icon_name = "gtk-dialog-authentication"
        dialog.props.secondary_use_markup = True
        dialog.props.title = _("Confirm value")
        dialog.props.text = _("Pairing with: %s") % alias
        dialog.props.secondary_text = _("Confirm value for authentication:") + "<b>%s</b>" % passkey
        resp = dialog.run()
        if resp == gtk.RESPONSE_YES:
            ok()
        else:
            err(AgentErrorRejected())

        dialog.destroy()
