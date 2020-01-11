# coding=utf-8
import os.path
import logging
from locale import bind_textdomain_codeset
from html import escape
import random
from xml.etree import ElementTree

import blueman.bluez as bluez
from blueman.Sdp import ServiceUUID
from blueman.Constants import *
from blueman.gui.Notification import Notification
from blueman.main.DbusService import DbusService, DbusError

from gi.repository import Gio

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def bt_class_to_string(bt_class):
    n1 = (bt_class & 0x1f00) >> 8
    if n1 == 0x03:
        return "network"
    elif n1 == 0x04:
        n2 = (bt_class & 0xfc) >> 2
        if n2 in (0x01, 0x02):
            return "headset"
        elif n2 == 0x06:
            return "headphone"
        else:
            return "audio"
    elif n1 == 0x05:
        n2 = (bt_class & 0xc0) >> 6
        if n2 == 0x00:
            n3 = (bt_class & 0x1e) >> 2
            if n3 in [0x01, 0x02]:
                return "joypad"
        elif n2 == 0x01:
            return "keyboard"
        elif n2 == 0x02:
            n3 = (bt_class & 0x1e) >> 2
            if n3 == 0x05:
                return "tablet"
            else:
                return "mouse"
    elif n1 == 0x06:
        if bt_class & 0x80:
            return "printer"
    else:
        return None


PIN_SEARCHES = [
    "./device[@oui='{oui}'][@type='{type}'][@name='{name}']",
    "./device[@oui='{oui}'][@type='{type}']",
    "./device[@oui='{oui}'][@name='{name}']",
    "./device[@type='{type}'][@name='{name}']",
    "./device[@oui='{oui}']",
    "./device[@name='{name}']",
    "./device[@type='{type}']",
]


class BluezErrorCanceled(DbusError):
    _name = "org.bluez.Error.Canceled"


class BluezErrorRejected(DbusError):
    _name = "org.bluez.Error.Rejected"


class BluezAgent(DbusService):
    __agent_path = '/org/bluez/agent/blueman'

    def __init__(self):
        super().__init__(None, "org.bluez.Agent1", self.__agent_path, Gio.BusType.SYSTEM)

        self.add_method("Release", (), "", self._on_release)
        self.add_method("RequestPinCode", ("o",), "s", self._on_request_pin_code, is_async=True)
        self.add_method("DisplayPinCode", ("o", "s"), "", self._on_display_pin_code)
        self.add_method("RequestPasskey", ("o",), "u", self._on_request_passkey, is_async=True)
        self.add_method("DisplayPasskey", ("o", "u", "y"), "", self._on_display_passkey)
        self.add_method("RequestConfirmation", ("o", "u"), "", self._on_request_confirmation, is_async=True)
        self.add_method("RequestAuthorization", ("o",), "", self._on_request_authorization, is_async=True)
        self.add_method("AuthorizeService", ("o", "s"), "", self._on_authorize_service, is_async=True)
        self.add_method("Cancel", (), "", self._on_cancel)

        self.dialog = None
        self.n = None
        self.signal_id = None
        self._db = None

    def register_agent(self):
        logging.info("Register Agent")
        self.register()
        bluez.AgentManager().register_agent(self.__agent_path, "KeyboardDisplay", default=True)

    def unregister_agent(self):
        logging.info("Unregister Agent")
        self.unregister()
        bluez.AgentManager().unregister_agent(self.__agent_path)

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
        if is_numeric:
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

        return dialog, pin_entry

    def get_device_string(self, device_path):
        device = bluez.Device(device_path)
        return "<b>%s</b> (%s)" % (escape(device["Alias"]), device["Address"])

    def _lookup_default_pin(self, device_path):
        if not self._db:
            self._db = ElementTree.parse(os.path.join(PKGDATA_DIR, 'pin-code-database.xml'))

        device = bluez.Device(device_path)
        lookup_dict = {
            'name': device['Name'],
            'type': bt_class_to_string(device['Class']),
            'oui': device['Address'][:9]
        }

        pin = None
        for s in PIN_SEARCHES:
            search = s.format(**lookup_dict)
            entry = self._db.find(search)
            if entry is not None:
                pin = entry.get('pin')
                break

        if pin is not None:
            if 'max:' in pin:
                pin = "".join(random.sample('123456789', int(pin[-1])))
        return pin

    def ask_passkey(self, dialog_msg, notify_msg, is_numeric, notification, device_path, ok, err):
        def passkey_dialog_cb(dialog, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                ret = pin_entry.get_text()
                ok(int(ret) if is_numeric else ret)
            else:
                err(BluezErrorRejected("Rejected"))
            dialog.destroy()
            self.dialog = None

        dev_str = self.get_device_string(device_path)
        notify_message = _("Pairing request for %s") % dev_str

        if self.dialog:
            logging.info("Agent: Another dialog still active, cancelling")
            err(BluezErrorCanceled("Canceled"))

        self.dialog, pin_entry = self.build_passkey_dialog(dev_str, dialog_msg, is_numeric)
        if not self.dialog:
            logging.error("Agent: Failed to build dialog")
            err(BluezErrorCanceled("Canceled"))

        if notification:
            Notification(_("Bluetooth Authentication"), notify_message, icon_name="blueman").show()

        self.dialog.connect("response", passkey_dialog_cb)
        self.dialog.present()

    # Workaround BlueZ not calling the Cancel method, see #164
    def _on_device_property_changed(self, device, key, value, path):
        if (key == "Paired" and value) or (key == "Connected" and not value):
            device.disconnect_signal(self.signal_id)
            self._on_cancel()

    def _on_release(self):
        logging.info("Agent.Release")
        self._on_cancel()
        self.unregister()

    def _on_cancel(self):
        logging.info("Agent.Cancel")
        if self.dialog:
            self.dialog.response(Gtk.ResponseType.REJECT)
        try:
            self.n.close()
        except AttributeError:
            pass

    def _on_request_pin_code(self, device_path, ok, err):
        logging.info("Agent.RequestPinCode")
        dialog_msg = _("Enter PIN code for authentication:")
        notify_msg = _("Enter PIN code")

        default_pin = self._lookup_default_pin(device_path)
        if default_pin is not None:
            logging.info('Sending default pin: %s' % default_pin)
            return default_pin

        self.ask_passkey(dialog_msg, notify_msg, False, True, device_path, ok, err)
        if self.dialog:
            self.dialog.present()

    def _on_request_passkey(self, device, ok, err):
        logging.info("Agent.RequestPasskey")
        dialog_msg = _("Enter passkey for authentication:")
        notify_msg = _("Enter passkey")
        self.ask_passkey(dialog_msg, notify_msg, True, True, device, ok, err)
        if self.dialog:
            self.dialog.present()

    def _on_display_passkey(self, device, passkey, _entered):
        logging.info('DisplayPasskey (%s, %d)' % (device, passkey))
        dev = bluez.Device(device)
        self.signal_id = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing passkey for") + " %s: %s" % (self.get_device_string(device), passkey)
        self.n = Notification("Bluetooth", notify_message, 0, icon_name="blueman")
        self.n.show()

    def _on_display_pin_code(self, device, pin_code):
        logging.info('DisplayPinCode (%s, %s)' % (device, pin_code))
        dev = bluez.Device(device)
        self.signal_id = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing PIN code for") + " %s: %s" % (self.get_device_string(device), pin_code)
        self.n = Notification("Bluetooth", notify_message, 0, icon_name="blueman")
        self.n.show()

    def _on_request_confirmation(self, device_path, passkey, ok, err):
        def on_confirm_action(action):
            if action == "confirm":
                ok()
            else:
                err(BluezErrorCanceled("User canceled pairing"))

        logging.info("Agent.RequestConfirmation")
        notify_message = _("Pairing request for:") + "\n%s" % self.get_device_string(device_path)

        if passkey:
            notify_message += "\n" + _("Confirm value for authentication:") + " <b>%s</b>" % passkey
        actions = [["confirm", _("Confirm")], ["deny", _("Deny")]]

        self.n = Notification("Bluetooth", notify_message, 0, actions, on_confirm_action, icon_name="blueman")
        self.n.show()

    def _on_request_authorization(self, device, ok, err):
        self._on_request_confirmation(device, None, ok, err)

    def _on_authorize_service(self, device, uuid, ok, err):
        def on_auth_action(action):
            logging.info(action)

            if action == "always":
                device = bluez.Device(n._device)
                device.set("Trusted", True)
            if action == "always" or action == "accept":
                ok()
            else:
                err(BluezErrorRejected("Rejected"))

            self.n = None

        logging.info("Agent.Authorize")
        dev_str = self.get_device_string(device)
        service = ServiceUUID(uuid).name
        notify_message = \
            (_("Authorization request for:") + "\n%s\n" + _("Service:") + " <b>%s</b>") % (dev_str, service)
        actions = [["always", _("Always accept")],
                   ["accept", _("Accept")],
                   ["deny", _("Deny")]]

        n = Notification(_("Bluetooth Authentication"), notify_message, 0, actions, on_auth_action, icon_name="blueman")
        n.show()
        n._device = device
