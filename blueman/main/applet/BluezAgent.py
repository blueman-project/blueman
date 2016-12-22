# coding=utf-8
import os.path
import logging
from locale import bind_textdomain_codeset

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib

from html import escape

import random
from xml.etree import ElementTree
import blueman.bluez as Bluez
from blueman.Sdp import ServiceUUID
from blueman.Constants import *
from blueman.gui.Notification import Notification

from blueman.bluez.Agent import Agent


def bt_class_to_string(bt_class):
    n1 =  (bt_class & 0x1f00) >> 8
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

class BluezAgent(Agent):
    __agent_path = '/org/bluez/agent/blueman'

    def __init__(self, time_func):
        super(BluezAgent, self).__init__(self.__agent_path, self._handle_method_call)

        self.dialog = None
        self.n = None
        self.signal_id = None
        self.time_func = time_func
        self._db = None

    def register_agent(self):
        logging.info("Register Agent")
        self._register_object()
        Bluez.AgentManager().register_agent(self.__agent_path, "KeyboardDisplay", default=True)

    def unregister_agent(self):
        logging.info("Unregister Agent")
        self._unregister_object()
        Bluez.AgentManager().unregister_agent(self.__agent_path)

    def _handle_method_call(self, connection, sender, agent_path, interface_name, method_name, parameters, invocation):

        if method_name == 'Release':
            self._on_release()
        elif method_name == 'RequestPinCode':
            self._on_request_pin_code(parameters, invocation)
        elif method_name == 'DisplayPinCode':
            self._on_display_pin_code(parameters, invocation)
        elif method_name == 'RequestPasskey':
            self._on_request_passkey(parameters, invocation)
        elif method_name == 'DisplayPasskey':
            self._on_display_passkey(parameters, invocation)
        elif method_name == 'RequestConfirmation':
            self._on_request_confirmation(parameters, invocation)
        elif method_name == 'RequestAuthorization':
            self._on_request_authorization(parameters, invocation)
        elif method_name == 'AuthorizeService':
            self._on_authorize_service(parameters, invocation)
        elif method_name == 'Cancel':
            self._on_cancel()
        else:
            logging.warning('Unhandled method: %s' % method_name)

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

    def get_device_string(self, device_path):
        device = Bluez.Device(device_path)
        return "<b>%s</b> (%s)" % (escape(device["Alias"]), device["Address"])

    def _lookup_default_pin(self, device_path):
        if not self._db:
            self._db = ElementTree.parse(os.path.join(PKGDATA_DIR, 'pin-code-database.xml'))

        device = Bluez.Device(device_path)
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

    def ask_passkey(self, dialog_msg, notify_msg, is_numeric, notification, parameters, invocation):
        device_path = parameters.unpack()[0]

        def passkey_dialog_cb(dialog, response_id):
            if response_id == Gtk.ResponseType.ACCEPT:
                ret = pin_entry.get_text()
                if is_numeric:
                    ret = GLib.Variant('(u)', int(ret))
                invocation.return_value(GLib.Variant('(s)', (ret,)))
            else:
                invocation.return_dbus_error('org.bluez.Error.Rejected', 'Rejected')
            dialog.destroy()
            self.dialog = None

        dev_str = self.get_device_string(device_path)
        notify_message = _("Pairing request for %s") % dev_str

        if self.dialog:
            logging.info("Agent: Another dialog still active, cancelling")
            invocation.return_dbus_error('org.bluez.Error.Canceled', 'Canceled')

        self.dialog, pin_entry = self.build_passkey_dialog(dev_str, dialog_msg, is_numeric)
        if not self.dialog:
            logging.error("Agent: Failed to build dialog")
            invocation.return_dbus_error('org.bluez.Error.Canceled', 'Canceled')

        if notification:
            Notification(_("Bluetooth Authentication"), notify_message, icon_name="blueman")

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
        self._unregister_object()

    def _on_cancel(self):
        logging.info("Agent.Cancel")
        if self.dialog:
            self.dialog.response(Gtk.ResponseType.REJECT)
        try:
            self.n.close()
        except AttributeError:
            pass


    def _on_request_pin_code(self, parameters, invocation):
        logging.info("Agent.RequestPinCode")
        dialog_msg = _("Enter PIN code for authentication:")
        notify_msg = _("Enter PIN code")

        object_path = parameters.unpack()[0]
        default_pin = self._lookup_default_pin(object_path)
        if default_pin is not None:
            logging.info('Sending default pin: %s' % default_pin)
            invocation.return_value(GLib.Variant('(s)', (default_pin,)))
            return

        self.ask_passkey(dialog_msg, notify_msg, False, True, parameters, invocation)
        if self.dialog:
            self.dialog.present_with_time(self.time_func())

    def _on_request_passkey(self, parameters, invocation):
        logging.info("Agent.RequestPasskey")
        dialog_msg = _("Enter passkey for authentication:")
        notify_msg = _("Enter passkey")
        self.ask_passkey(dialog_msg, notify_msg, True, True, parameters, invocation)
        if self.dialog:
            self.dialog.present_with_time(self.time_func())

    def _on_display_passkey(self, parameters, invocation):
        device, passkey, entered = parameters.unpack()
        logging.info('DisplayPasskey (%s, %d)' % (device, passkey))
        dev = Bluez.Device(device)
        self.signal_id = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing passkey for") + " %s: %s" % (self.get_device_string(device), passkey)
        self.n = Notification("Bluetooth", notify_message, 0, icon_name="blueman")
        self.n.show()

    def _on_display_pin_code(self, parameters, invocation):
        device, pin_code = parameters.unpack()
        logging.info('DisplayPinCode (%s, %s)' % (device, pin_code))
        dev = Bluez.Device(device)
        self.signal_id = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing PIN code for") + " %s: %s" % (self.get_device_string(device), pin_code)
        self.n = Notification("Bluetooth", notify_message, 0, icon_name="blueman")
        self.n.show()

        invocation.return_value(None)

    def _on_request_confirmation(self, parameters, invocation):
        def on_confirm_action(action):
            if action == "confirm":
                invocation.return_value(GLib.Variant('()', ()))
            else:
                invocation.return_dbus_error('org.bluez.Error.Canceled', "User canceled pairing")

        params = parameters.unpack()
        if len(params) < 2:
            device_path = params[0]
            passkey = None
        else:
            device_path, passkey = params

        logging.info("Agent.RequestConfirmation")
        notify_message = _("Pairing request for:") + "\n%s" % self.get_device_string(device_path)

        if passkey:
            notify_message += "\n" + _("Confirm value for authentication:") + " <b>%s</b>" % passkey
        actions = [["confirm", _("Confirm")], ["deny", _("Deny")]]

        self.n = Notification("Bluetooth", notify_message, 0, actions, on_confirm_action, icon_name="blueman")
        self.n.show()

    def _on_request_authorization(self, parameters, invocation):
        self._on_request_confirmation(parameters, invocation)

    def _on_authorize_service(self, parameters, invocation):
        def on_auth_action(action):
            logging.info(action)

            if action == "always":
                device = Bluez.Device(n._device)
                device.set("Trusted", True)
            if action == "always" or action == "accept":
                invocation.return_value(GLib.Variant('()', ()))
            else:
                invocation.return_dbus_error('org.bluez.Error.Rejected', 'Rejected')

            self.n = None

        device, uuid = parameters.unpack()

        logging.info("Agent.Authorize")
        dev_str = self.get_device_string(device)
        service = ServiceUUID(uuid).name
        notify_message = (_("Authorization request for:") + "\n%s\n" + _("Service:") + " <b>%s</b>") % (dev_str, service)
        actions = [["always", _("Always accept")],
                   ["accept", _("Accept")],
                   ["deny", _("Deny")]]

        n = Notification(_("Bluetooth Authentication"), notify_message, 0, actions, on_auth_action, icon_name="blueman")
        n.show()
        n._device = device
