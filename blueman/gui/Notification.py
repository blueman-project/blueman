from typing import Dict, List, Callable, Optional, Iterable, Tuple, Union, Type

from blueman.main.Config import Config

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GLib
from gi.repository import Gio
from blueman.gui.GtkAnimation import AnimBase
import logging

OPACITY_START = 0.7


class Fade(AnimBase):
    def __init__(self, window: Gtk.Window) -> None:
        super().__init__(state=OPACITY_START)
        self.window = window

    def state_changed(self, state: float) -> None:
        self.window.props.opacity = state


class _NotificationDialog(Gtk.MessageDialog):
    def __init__(self, summary: str, message: str, _timeout: int = -1,
                 actions: Optional[Iterable[Tuple[str, str]]] = None,
                 actions_cb: Optional[Callable[[str], None]] = None, icon_name: Optional[str] = None,
                 image_data: Optional[GdkPixbuf.Pixbuf] = None) -> None:
        super().__init__(parent=None, type=Gtk.MessageType.QUESTION,
                         buttons=Gtk.ButtonsType.NONE, text=None)

        self.set_name("NotificationDialog")
        i = 100
        self.actions_supported = True
        self.actions: Dict[int, str] = {}
        self.callback = actions_cb
        if actions:
            for a in actions:
                action_id = a[0]
                action_name = a[1]

                self.actions[i] = action_id
                self.add_button(action_name, i)
                i += 1

        self.actions[Gtk.ResponseType.DELETE_EVENT] = "close"

        self.props.secondary_use_markup = True
        self.resize(350, 50)

        self.fader = Fade(self)

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

        self.entered = False

        def on_enter(_widget: "_NotificationDialog", _event: Gdk.Event) -> bool:
            if self.get_window() == Gdk.Window.at_pointer()[0] or not self.entered:
                self.fader.animate(start=self.fader.get_state(), end=1.0, duration=500)
                self.entered = True
            return False

        def on_leave(_widget: "_NotificationDialog", _event: Gdk.Event) -> bool:
            if not Gdk.Window.at_pointer():
                self.entered = False
                self.fader.animate(start=self.fader.get_state(), end=OPACITY_START, duration=500)
            return False

        self.connect("enter-notify-event", on_enter)
        self.connect("leave-notify-event", on_leave)

    def dialog_response(self, _dialog: Gtk.Dialog, response: int) -> None:
        if self.callback:
            self.callback(self.actions[response])
        self.hide()

    def show(self) -> None:
        self.set_opacity(OPACITY_START)
        self.present()
        self.set_opacity(OPACITY_START)

    def close(self) -> None:
        self.hide()

    def add_action(self, _action_id: str, _label: str, _callback: Optional[Callable[[str], None]] = None) -> None:
        logging.warning("stub")

    def set_icon_from_pixbuf(self, pixbuf: GdkPixbuf.Pixbuf) -> None:
        im = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_image(im)
        im.show()

    def set_icon_from_icon_name(self, icon_name: str, size: int) -> None:
        im = Gtk.Image(icon_name=icon_name, pixel_size=size)
        self.set_image(im)
        im.show()


class _NotificationBubble(Gio.DBusProxy):
    def __init__(self, summary: str, message: str, timeout: int = -1,
                 actions: Optional[Iterable[Tuple[str, str]]] = None,
                 actions_cb: Optional[Callable[[str], None]] = None, icon_name: Optional[str] = None,
                 image_data: Optional[GdkPixbuf.Pixbuf] = None) -> None:
        super().__init__(
            g_name='org.freedesktop.Notifications',
            g_interface_name='org.freedesktop.Notifications',
            g_object_path='/org/freedesktop/Notifications',
            g_bus_type=Gio.BusType.SESSION,
            g_flags=Gio.DBusProxyFlags.NONE)

        self.init()

        self._app_name = 'blueman'
        self._app_icon = ''
        self._actions: List[str] = []
        self._callbacks: Dict[str, Callable[[str], None]] = {}
        self._hints: Dict[str, GLib.Variant] = {}

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

        if actions:
            for action in actions:
                self.add_action(action[0], action[1], actions_cb)

        self._capabilities = self.GetCapabilities()

    @property
    def server_information(self) -> Tuple[str, str, str, str]:
        info: Tuple[str, str, str, str] = self.GetServerInformation()
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

    def add_action(self, action_id: str, label: str, callback: Optional[Callable[[str], None]] = None) -> None:
        self._actions.extend([action_id, label])
        if callback:
            self._callbacks[action_id] = callback

    def clear_actions(self) -> None:
        self._actions = []
        self._callbacks = {}

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
            if signal_val in self._callbacks:
                self._callbacks[signal_val](signal_val)

    def show(self) -> None:
        replace_id = self._return_id if self._return_id else 0
        return_id = self.Notify('(susssasa{sv}i)', self._app_name, replace_id, self._app_icon,
                                self._summary, self._body, self._actions, self._hints,
                                self._timeout)
        self._return_id = return_id

    def close(self) -> None:
        param = GLib.Variant('(u)', (self._return_id,))
        self.call_sync('CloseNotification', param, Gio.DBusCallFlags.NONE, -1, None)
        self._return_id = None


def Notification(summary: str, message: str, timeout: int = -1, actions: Optional[Iterable[Tuple[str, str]]] = None,
                 actions_cb: Optional[Callable[[str], None]] = None, icon_name: Optional[str] = None,
                 image_data: Optional[GdkPixbuf.Pixbuf] = None) -> Union[_NotificationBubble, _NotificationDialog]:

    forced_fallback = not Config('org.blueman.general')['notification-daemon']
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
        klass: Type[Union[_NotificationBubble, _NotificationDialog]] = _NotificationDialog
    else:
        klass = _NotificationBubble

    return klass(summary, message, timeout, actions, actions_cb, icon_name, image_data)
