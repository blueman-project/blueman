from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from dbus.mainloop.glib import DBusGMainLoop
import dbus.service
from locale import bind_textdomain_codeset
from blueman.Functions import get_icon, dprint

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject
from gi.types import GObjectMeta
import cgi
import blueman.bluez as Bluez
from blueman.Sdp import *
from blueman.Constants import *
from blueman.gui.Notification import Notification

from blueman.bluez.Agent import Agent, AgentMethod

DBusGMainLoop(set_as_default=True)


class AgentErrorRejected(dbus.DBusException):
    def __init__(self):
        super(AgentErrorRejected, self).__init__(name="org.bluez.Error.Rejected")


class AgentErrorCanceled(dbus.DBusException):
    def __init__(self):
        super(AgentErrorCanceled, self).__init__(name="org.bluez.Error.Canceled")


class _GDbusObjectType(dbus.service.InterfaceType, GObjectMeta):
    pass

_GObjectAgent = _GDbusObjectType(str('_GObjectAgent'), (Agent, GObject.GObject), {})


class BluezAgent(_GObjectAgent, Agent, GObject.GObject):
    __gsignals__ = {
        str('released'): (GObject.SignalFlags.NO_HOOKS, None, ()),
    }

    def __init__(self, status_icon, time_func):
        Agent.__init__(self, '/org/blueman/agent/bluez_agent')
        GObject.GObject.__init__(self)

        self.status_icon = status_icon
        self.dialog = None
        self.n = None
        self.signal_id = None
        self.time_func = time_func

        Bluez.AgentManager().register_agent(self, "KeyboardDisplay", default=True)

    def __del__(self):
        dprint()
        Bluez.AgentManager().unregister_agent(self)

    def build_passkey_dialog(self, device_alias, dialog_msg, is_numeric):
        def on_insert_text(editable, new_text, new_text_length, position):
            if not new_text.isdigit():
                editable.stop_emission("insert-text")

        builder = Gtk.Builder()
        builder.add_from_file(UI_PATH + "/applet-passkey.ui")
        builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
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
        props = device.get_properties()
        address = props["Address"]
        name = props.get('Name', address)
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
                    self.dialog.response(Gtk.ResponseType.REJECT)
                #self.applet.status_icon.set_blinking(False)


        def passkey_dialog_cb(dialog, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
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

    # Workaround BlueZ not calling the Cancel method, see #164
    def _on_device_property_changed(self, device, key, value, path):
        if (key == "Paired" and value) or (key == "Connected" and not value):
            device.disconnect_signal(self.signal_id)
            self.Cancel()

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
            self.dialog.response(Gtk.ResponseType.REJECT)
        try:
            self.n.close()
        except AttributeError:
            pass

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
        dprint('DisplayPasskey (%s, %d)' % (device, passkey))
        dev = Bluez.Device(device)
        self.signal_id = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing passkey for") + " %s: %s" % (self.get_device_alias(device), passkey)
        self.n = Notification("Bluetooth", notify_message, 0,
                              pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)

    @AgentMethod
    def DisplayPinCode(self, device, pin_code):
        dprint('DisplayPinCode (%s, %s)' % (device, pin_code))
        dev = Bluez.Device(device)
        self.signal_id = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing PIN code for") + " %s: %s" % (self.get_device_alias(device), pin_code)
        self.n = Notification("Bluetooth", notify_message, 0,
                              pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)

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
        notify_message = _("Pairing request for:") + "\n%s" % alias
        if passkey:
            notify_message += "\n" + _("Confirm value for authentication:") + " <b>%s</b>" % passkey
        actions = [["confirm", _("Confirm")], ["deny", _("Deny")]]

        Notification("Bluetooth", notify_message, 0,
                     actions, on_confirm_action,
                     pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)

    @AgentMethod
    def RequestAuthorization(self, device, ok, err):
        self.RequestConfirmation(device, None, ok, err)

    @AgentMethod
    def Authorize(self, device, uuid, ok, err):

        def on_auth_action(n, action):
            dprint(action)

            #self.applet.status_icon.set_blinking(False)
            if action == "always":
                device = Bluez.Device(n._device)
                device.set("Trusted", True)
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
        actions = [["always", _("Always accept")],
                   ["accept", _("Accept")],
                   ["deny", _("Deny")]]

        n = Notification(_("Bluetooth Authentication"), notify_message, 0,
                         actions, on_auth_action,
                         pixbuf=get_icon("blueman", 48), status_icon=self.status_icon)
        n._device = device

    @AgentMethod
    def AuthorizeService(self, device, uuid, ok, err):
        self.Authorize(device, uuid, ok, err)
