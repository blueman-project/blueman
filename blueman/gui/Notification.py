from collections.abc import Callable, Iterable
from gettext import gettext as _
from typing import NamedTuple

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gio
import logging


class NotificationAction(NamedTuple):
    id: str
    name: str
    callback: Callable[[str], None] | None = None


class _NotificationDialog(Gtk.MessageDialog):
    def __init__(self, summary: str, message: str, _timeout: int = -1, _transient: bool = False,
                 actions: Iterable[NotificationAction] | None = None, icon_name: str | None = None,
                 image_data: GdkPixbuf.Pixbuf | None = None) -> None:
        super().__init__(parent=None, type=Gtk.MessageType.QUESTION,
                         buttons=Gtk.ButtonsType.NONE, text=None)

        self.set_name("NotificationDialog")
        self.actions_supported = True
        self.actions: dict[int, NotificationAction] = {}

        if actions is None:
            actions = [NotificationAction("close", _("_Close"), lambda s: self.close())]

        for action in actions:
            self.add_action(action)

        self.props.secondary_use_markup = True
        self.resize(350, 50)

        self.props.skip_taskbar_hint = False

        self.props.title = summary
        self.props.text = summary
        self.props.secondary_text = message

        self.props.window_position = Gtk.WindowPosition.CENTER

        if icon_name:
            self.set_icon_from_icon_name(icon_name, 48)
        elif image_data:
            self.set_icon_from_pixbuf(image_data)

        self.connect("response", self.dialog_response)
        self.props.icon_name = "blueman"

    def set_message(self, message: str) -> None:
        self.props.secondary_text = message

    def set_notification_icon(self, icon_name: str) -> None:
        self.set_icon_from_icon_name(icon_name, 48)

    def dialog_response(self, _dialog: Gtk.Dialog, response: int) -> None:
        action = self.actions.pop(response, None)
        if action is None:
            logging.error(f"Unhandled response {response}")
            return

        if action.callback is not None:
            action.callback(action.id)
        self.destroy()

    def show(self) -> None:
        self.present()

    def close(self) -> None:
        self.destroy()

    def add_action(self, action: NotificationAction) -> None:
        if not self.actions:
            response_id = 100
        else:
            response_id = max(self.actions.keys()) + 1

        self.actions[response_id] = action
        self.add_button(action.name, response_id)

    def set_icon_from_pixbuf(self, pixbuf: GdkPixbuf.Pixbuf) -> None:
        im = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_image(im)
        im.show()

    def set_icon_from_icon_name(self, icon_name: str, size: int) -> None:
        im = Gtk.Image(icon_name=icon_name, pixel_size=size)
        self.set_image(im)
        im.show()


class _NotificationBubble(Gio.DBusProxy):
    def __init__(self, summary: str, message: str, timeout: int = -1, transient: bool = False,
                 actions: Iterable[NotificationAction] | None = None, icon_name: str | None = None,
                 image_data: GdkPixbuf.Pixbuf | None = None) -> None:
        super().__init__(
            g_name='org.freedesktop.Notifications',
            g_interface_name='org.freedesktop.Notifications',
            g_object_path='/org/freedesktop/Notifications',
            g_bus_type=Gio.BusType.SESSION,
            g_flags=Gio.DBusProxyFlags.NONE)

        self.init()

        self._app_name = 'blueman'
        self._app_icon = ''
        self._actions: dict[str, NotificationAction] = {}
        self._notification_actions: list[str] = []
        self._hints: dict[str, GLib.Variant] = {}

        # hint : (variant format, spec version)
        self._supported_hints = {
            'action-icons': ('b', 1.2),
            'category': ('s', 0),
            'desktop-entry': ('s', 0),
            'image-data': ('(iiibiiay)', 1.2),
            'image_data': ('(iiibiiay)', 1.1),
            'image-path': ('s', 1.2),
            'image_path': ('s', 1.1),
            'icon_data': ('(iiibiiay)', 0),
            'resident': ('b', 1.2),
            'sound-file': ('s', 0),
            'sound-name': ('s', 0),
            'suppress-sound': ('b', 0),
            'transient': ('b', 1.2),
            'x': ('i', 0),
            'y': ('i', 0),
            'urgency': ('y', 0)}

        self._body = message
        self._summary = summary
        self._timeout = timeout
        self._return_id = None

        if transient:
            try:
                self.set_hint('transient', True)
            except ValueError:
                pass

        if icon_name:
            self._app_icon = icon_name
        elif image_data:
            w = image_data.props.width
            h = image_data.props.height
            stride = image_data.props.rowstride
            alpha = image_data.props.has_alpha
            bits = image_data.props.bits_per_sample
            channel = image_data.props.n_channels
            data = image_data.get_pixels()
            supported_spec = float(self.server_information[-1])
            if supported_spec < 1.1:
                key = 'icon_data'
            elif supported_spec < 1.2:
                key = 'image_data'
            elif supported_spec >= 1.2:
                key = 'image-data'
            else:
                raise ValueError('Not supported by server')

            self.set_hint(key, (w, h, stride, alpha, bits, channel, data))

        if actions is not None:
            for action in actions:
                self.add_action(action)

        self._capabilities = self.GetCapabilities()

    def set_message(self, message: str) -> None:
        self._body = message
        if self._return_id is not None:
            self.show()

    def set_notification_icon(self, icon_name: str) -> None:
        self._app_icon = icon_name
        if self._return_id is not None:
            self.show()

    @property
    def server_information(self) -> tuple[str, str, str, str]:
        info: tuple[str, str, str, str] = self.GetServerInformation()
        return info

    @property
    def actions_supported(self) -> bool:
        return 'actions' in self._capabilities

    def set_hint(self, key: str, val: object) -> None:
        if key not in self._supported_hints:
            raise ValueError('Unsupported hint')
        fmt, spec_version = self._supported_hints[key]
        if spec_version > float(self.server_information[-1]):
            raise ValueError('Not supported by server')

        param = GLib.Variant(fmt, val)
        self._hints[key] = param

    def remove_hint(self, key: str) -> None:
        del (self._hints[key])

    def clear_hints(self) -> None:
        self._hints = {}

    def add_action(self, action: NotificationAction) -> None:
        self._actions[action.id] = action
        self._notification_actions.extend([action.id, action.name])

    def clear_actions(self) -> None:
        self._actions.clear()
        self._notification_actions.clear()

    def do_g_signal(self, _sender_name: str, signal_name: str, params: GLib.Variant) -> None:
        notif_id, signal_val = params.unpack()
        if notif_id != self._return_id:
            return

        logging.info(signal_val)

        if signal_name == 'NotificationClosed':
            if signal_val == 1:
                logging.debug('The notification expired.')
            elif signal_val == 2:
                logging.debug('The notification was dismissed by the user.')
            elif signal_val == 3:
                logging.debug('The notification was closed by a call to CloseNotification.')
            elif signal_val == 4:
                logging.debug('Undefined/reserved reasons.')
        elif signal_name == 'ActionInvoked':
            action = self._actions.pop(signal_val, None)
            if action is None:
                logging.error(f"Unhandled action {signal_val}")
                return

            if action.callback is not None:
                action.callback(action.id)

    def show(self) -> None:
        replace_id = self._return_id if self._return_id else 0
        return_id = self.Notify('(susssasa{sv}i)', self._app_name, replace_id, self._app_icon,
                                self._summary, self._body, self._notification_actions, self._hints,
                                self._timeout)
        self._return_id = return_id

    def close(self) -> None:
        param = GLib.Variant('(u)', (self._return_id,))
        self.call_sync('CloseNotification', param, Gio.DBusCallFlags.NONE, -1, None)
        self._return_id = None


def Notification(
    summary: str,
    message: str,
    timeout: int = -1,
    transient: bool = False,
    actions: Iterable[NotificationAction] | None = None,
    icon_name: str | None = None,
    image_data: GdkPixbuf.Pixbuf | None = None
) -> _NotificationBubble | _NotificationDialog:

    forced_fallback = not Gio.Settings(schema_id='org.blueman.general')['notification-daemon']
    try:
        bus = Gio.bus_get_sync(Gio.BusType.SESSION)
        caps = bus.call_sync('org.freedesktop.Notifications', '/org/freedesktop/Notifications',
                             'org.freedesktop.Notifications', 'GetCapabilities', None, None,
                             Gio.DBusCallFlags.NONE, -1, None).unpack()[0]
    except GLib.Error:
        caps = []

    if forced_fallback or 'body' not in caps or (actions and 'actions' not in caps):
        # Use fallback in the case:
        # * user does not want to use a notification daemon
        # * the notification daemon is not available
        # * we have to show actions and the notification daemon does not provide them
        klass: type[_NotificationBubble | _NotificationDialog] = _NotificationDialog
    else:
        klass = _NotificationBubble

    return klass(summary, message, timeout, transient, actions, icon_name, image_data)
