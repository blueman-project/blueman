from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.Config import Config

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version('Notify', '0.7')
from gi.repository import Notify
from gi.repository import Gtk
from gi.repository import Gdk
from blueman.Functions import dprint
from blueman.gui.GtkAnimation import AnimBase

Notify.init("blueman")

OPACITY_START = 0.7


class Fade(AnimBase):
    def __init__(self, window):
        AnimBase.__init__(self, state=OPACITY_START)
        self.window = window

    def state_changed(self, state):
        self.window.props.opacity = state


class _NotificationDialog(Gtk.MessageDialog):
    def __init__(self, summary, message, timeout=-1, actions=None, actions_cb=None, pixbuf=None, status_icon=None):
        Gtk.MessageDialog.__init__(self, parent=None, flags=0, type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.NONE, message_format=None)

        i = 100
        self.actions = {}
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

        if pixbuf:
            self.set_icon_from_pixbuf(pixbuf)

        self.connect("response", self.dialog_response)
        self.props.icon_name = "blueman"

        self.entered = False

        def on_enter(widget, event):
            if self.get_window() == Gdk.Window.at_pointer()[0] or not self.entered:
                self.fader.animate(start=self.fader.get_state(), end=1.0, duration=500)
                self.entered = True

        def on_leave(widget, event):
            if not Gdk.Window.at_pointer():
                self.entered = False
                self.fader.animate(start=self.fader.get_state(), end=OPACITY_START, duration=500)

        self.connect("enter-notify-event", on_enter)
        self.connect("leave-notify-event", on_leave)

        self.set_opacity(OPACITY_START)
        self.present()
        self.set_opacity(OPACITY_START)

    def dialog_response(self, dialog, response):
        if self.callback:
            self.callback(self, self.actions[response])
        self.hide()

    def close(self):
        self.hide()

    def set_hint_int32(self, *args):
        dprint("stub")

    def set_timeout(self, *args):
        dprint("stub")

    def add_action(self, *args):
        dprint("stub")

    def clear_actions(self, *args):
        dprint("stub")

    def set_urgency(self, *args):
        dprint("stub")

    def update(self, summary, message):
        self.props.title = summary

        self.props.text = summary
        self.props.secondary_text = message
        self.present()

    def set_icon_from_pixbuf(self, pixbuf):
        im = Gtk.Image.new_from_pixbuf(pixbuf)
        self.set_image(im)
        im.show()


class _NotificationBubble(Notify.Notification):
    def __new__(cls, summary, message, timeout=-1, actions=None, actions_cb=None, pixbuf=None, status_icon=None):
        self = Notify.Notification.new(summary, message, None)

        def on_notification_closed(n, *args):
            self.disconnect(closed_sig)
            if actions_cb:
                actions_cb(n, "closed")

        def on_action(n, action, *args):
            self.disconnect(closed_sig)
            actions_cb(n, action)

        if pixbuf:
            self.set_icon_from_pixbuf(pixbuf)

        if actions:
            for action in actions:
                self.add_action(action[0], action[1], on_action, None)
            self.add_action("default", "Default Action", on_action, None)

        closed_sig = self.connect("closed", on_notification_closed)
        if timeout != -1:
            self.set_timeout(timeout)
        if status_icon:
            ignored, screen, area, orientation = status_icon.get_geometry()
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            # Workaround a problem where we get garbage x and y values
            if (area.x > 0 and area.y > 0) and (area.x <= screen_width and area.y <= screen_height):
                self.set_hint_int32("x", area.x + area.width / 2)
                self.set_hint_int32("y", area.y + area.height / 2)
            else:
                dprint("Got bad x %s or y %s value" % (area.x, area.y))

        self.show()

        return self


class Notification(object):
    @staticmethod
    def actions_supported():
        return "actions" in Notify.get_server_caps()

    @staticmethod
    def body_supported():
        return "body" in Notify.get_server_caps()

    def __new__(cls, summary, message, timeout=-1, actions=None, actions_cb=None, pixbuf=None, status_icon=None):
        forced_fallback = not Config('org.blueman.general')['notification-daemon']

        if forced_fallback or not cls.body_supported() or (actions and not cls.actions_supported()):
            # Use fallback in the case:
            # * user does not want to use a notification daemon
            # * the notification daemon is not available
            # * we have to show actions and the notification daemon does not provide them
            klass = _NotificationDialog
        else:
            klass = _NotificationBubble

        return klass(summary, message, timeout, actions, actions_cb, pixbuf, status_icon)

    # stub to satisfy pylint
    def close(self):
        pass
