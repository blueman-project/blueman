import logging
from gettext import gettext as _
from html import escape
from xml.etree import ElementTree
from typing import Dict, Optional, overload, Callable, Union, TYPE_CHECKING, Tuple, Any, List

from blueman.bluez.Device import Device
from blueman.bluez.AgentManager import AgentManager
from blueman.Sdp import ServiceUUID
from blueman.gui.Notification import Notification, _NotificationBubble, _NotificationDialog
from blueman.main.Builder import Builder
from blueman.main.DbusService import DbusService, DbusError

from gi.repository import Gio

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from typing_extensions import Literal


class BluezErrorCanceled(DbusError):
    _name = "org.bluez.Error.Canceled"


class BluezErrorRejected(DbusError):
    _name = "org.bluez.Error.Rejected"


class BluezAgent(DbusService):
    __agent_path = '/org/bluez/agent/blueman'

    def __init__(self) -> None:
        super().__init__(None, "org.bluez.Agent1", self.__agent_path, Gio.BusType.SYSTEM)

        self.add_method("Release", (), "", self._on_release)
        self.add_method("RequestPinCode", ("o",), "s", self._on_request_pin_code, is_async=True)
        self.add_method("DisplayPinCode", ("o", "s"), "", self._on_display_pin_code)
        self.add_method("RequestPasskey", ("o",), "u", self._on_request_passkey, is_async=True)
        self.add_method("DisplayPasskey", ("o", "u", "q"), "", self._on_display_passkey)
        self.add_method("RequestConfirmation", ("o", "u"), "", self._on_request_confirmation, is_async=True)
        self.add_method("RequestAuthorization", ("o",), "", self._on_request_authorization, is_async=True)
        self.add_method("AuthorizeService", ("o", "s"), "", self._on_authorize_service, is_async=True)
        self.add_method("Cancel", (), "", self._on_cancel)

        self.dialog: Optional[Gtk.Dialog] = None
        self._db: Optional[ElementTree.ElementTree] = None
        self._devhandlerids: Dict[str, int] = {}
        self._notification: Optional[Union[_NotificationBubble, _NotificationDialog]] = None
        self._service_notifications: List[Union[_NotificationBubble, _NotificationDialog]] = []

    def register_agent(self) -> None:
        logging.info("Register Agent")
        self.register()
        AgentManager().register_agent(self.__agent_path, "KeyboardDisplay", default=True)

    def unregister_agent(self) -> None:
        logging.info("Unregister Agent")
        self.unregister()
        AgentManager().unregister_agent(self.__agent_path)

    def build_passkey_dialog(self, device_alias: str, dialog_msg: str, is_numeric: bool
                             ) -> Tuple[Gtk.Dialog, Gtk.Entry]:
        def on_insert_text(editable: Gtk.Entry, new_text: str, _new_text_length: int, _position: int) -> None:
            if not new_text.isdigit():
                editable.stop_emission("insert-text")

        builder = Builder("applet-passkey.ui")

        dialog = builder.get_widget("dialog", Gtk.Dialog)

        dialog.props.icon_name = "blueman"
        dev_name = builder.get_widget("device_name", Gtk.Label)
        dev_name.set_markup(device_alias)
        msg = builder.get_widget("message", Gtk.Label)
        msg.set_text(dialog_msg)
        pin_entry = builder.get_widget("pin_entry", Gtk.Entry)
        show_input = builder.get_widget("show_input_check", Gtk.CheckButton)
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
        accept_button = builder.get_widget("accept", Gtk.Button)
        pin_entry.connect("changed", lambda x: accept_button.set_sensitive(x.get_text() != ''))

        return dialog, pin_entry

    def get_device_string(self, device_path: str) -> str:
        device = Device(obj_path=device_path)
        return f"<b>{escape(device['Alias'])}</b> ({device['Address']})"

    @overload
    def ask_passkey(self, dialog_msg: str, is_numeric: "Literal[True]", device_path: str, ok: Callable[[int], None],
                    err: Callable[[Union[BluezErrorCanceled, BluezErrorRejected]], None]) -> None:
        ...

    @overload
    def ask_passkey(self, dialog_msg: str, is_numeric: "Literal[False]", device_path: str, ok: Callable[[str], None],
                    err: Callable[[Union[BluezErrorCanceled, BluezErrorRejected]], None]) -> None:
        ...

    def ask_passkey(self, dialog_msg: str, is_numeric: bool, device_path: str, ok: Callable[[Any], None],
                    err: Callable[[Union[BluezErrorCanceled, BluezErrorRejected]], None]) -> None:
        def passkey_dialog_cb(dialog: Gtk.Dialog, response_id: int) -> None:
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

        Notification(_("Bluetooth Authentication"), notify_message, icon_name="blueman").show()

        self.dialog.connect("response", passkey_dialog_cb)
        self.dialog.present()

    # Workaround BlueZ not calling the Cancel method, see #164
    def _on_device_property_changed(self, device: Device, key: str, value: Any, path: str) -> None:
        if (key == "Paired" and value) or (key == "Connected" and not value):
            handlerid = self._devhandlerids.pop(path)
            device.disconnect_signal(handlerid)
            self._on_cancel()

    def _on_release(self) -> None:
        logging.info("Agent.Release")
        self._on_cancel()
        self.unregister()

    def _on_cancel(self) -> None:
        logging.info("Agent.Cancel")
        if self.dialog:
            self.dialog.response(Gtk.ResponseType.REJECT)
        self._close()

    def _close(self) -> None:
        if self._notification is not None:
            self._notification.close()
            self._notification = None

    def _on_request_pin_code(self, device_path: str, ok: Callable[[str], None],
                             err: Callable[[Union[BluezErrorCanceled, BluezErrorRejected]], None]) -> None:
        logging.info("Agent.RequestPinCode")
        dialog_msg = _("Enter PIN code for authentication:")

        self.ask_passkey(dialog_msg, False, device_path, ok, err)
        if self.dialog:
            self.dialog.present()

    def _on_request_passkey(self, device: str, ok: Callable[[int], None],
                            err: Callable[[Union[BluezErrorCanceled, BluezErrorRejected]], None]) -> None:
        logging.info("Agent.RequestPasskey")
        dialog_msg = _("Enter passkey for authentication:")
        self.ask_passkey(dialog_msg, True, device, ok, err)
        if self.dialog:
            self.dialog.present()

    def _on_display_passkey(self, device: str, passkey: int, entered: int) -> None:
        logging.info(f"DisplayPasskey ({device}, {passkey:d} {entered:d})")
        dev = Device(obj_path=device)
        self._devhandlerids[device] = dev.connect_signal("property-changed", self._on_device_property_changed)

        key = f"{passkey:06}"
        notify_message = _("Pairing passkey for") + f" {self.get_device_string(device)}: " \
                                                    f"{key[:entered]}<b>{key[entered]}</b>{key[entered+1:]}"
        self._close()
        self._notification = Notification("Bluetooth", notify_message, 0, icon_name="blueman")
        self._notification.show()

    def _on_display_pin_code(self, device: str, pin_code: str) -> None:
        logging.info(f'DisplayPinCode ({device}, {pin_code})')
        dev = Device(obj_path=device)
        self._devhandlerids[device] = dev.connect_signal("property-changed", self._on_device_property_changed)

        notify_message = _("Pairing PIN code for") + f" {self.get_device_string(device)}: {pin_code}"
        self._notification = Notification("Bluetooth", notify_message, 0, icon_name="blueman")
        self._notification.show()

    def _on_request_confirmation(self, device_path: str, passkey: Optional[int], ok: Callable[[], None],
                                 err: Callable[[BluezErrorCanceled], None]) -> None:
        def on_confirm_action(action: str) -> None:
            if action == "confirm":
                ok()
            else:
                err(BluezErrorCanceled("User canceled pairing"))

        logging.info("Agent.RequestConfirmation")
        notify_message = _("Pairing request for:") + f"\n{self.get_device_string(device_path)}"

        if passkey:
            notify_message += "\n" + _("Confirm value for authentication:") + f" <b>{passkey:06}</b>"
        actions = [("confirm", _("Confirm")), ("deny", _("Deny"))]

        self._notification = Notification("Bluetooth", notify_message, 0, actions, on_confirm_action,
                                          icon_name="blueman")
        self._notification.show()

    def _on_request_authorization(self, device: str, ok: Callable[[], None],
                                  err: Callable[[BluezErrorCanceled], None]) -> None:
        self._on_request_confirmation(device, None, ok, err)

    def _on_authorize_service(self, device: str, uuid: str, ok: Callable[[], None],
                              err: Callable[[BluezErrorRejected], None]) -> None:
        def on_auth_action(action: str) -> None:
            logging.info(action)

            if action == "always":
                Device(obj_path=device).set("Trusted", True)
            if action == "always" or action == "accept":
                ok()
            else:
                err(BluezErrorRejected("Rejected"))

            self._service_notifications.remove(n)

        logging.info("Agent.Authorize")
        dev_str = self.get_device_string(device)
        service = ServiceUUID(uuid).name
        notify_message = \
            _("Authorization request for:") + f"\n{dev_str}\n" + _("Service:") + f" <b>{service}</b>"
        actions = [("always", _("Always accept")),
                   ("accept", _("Accept")),
                   ("deny", _("Deny"))]

        n = Notification(_("Bluetooth Authentication"), notify_message, 0, actions, on_auth_action, icon_name="blueman")
        n.show()
        self._service_notifications.append(n)
