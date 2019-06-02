# coding=utf-8
import logging

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib


class ManagerProgressbar(GObject.GObject):
    __gsignals__ = {
        'cancelled': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    __instances__ = []

    def __init__(self, blueman, cancellable=True, text=_("Connecting")):
        super().__init__()
        self.Blueman = blueman

        self.cancellable = cancellable

        self.hbox = hbox = blueman.Builder.get_object("status_data")

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_name("ManagerProgressbar")

        self._signals = []

        self.button = Gtk.Image(icon_name="process-stop", pixel_size=16)

        self.eventbox = eventbox = Gtk.EventBox()
        eventbox.add(self.button)
        eventbox.props.tooltip_text = _("Cancel Operation")
        eventbox.connect("enter-notify-event", self._on_enter)
        eventbox.connect("leave-notify-event", self._on_leave)
        eventbox.connect("button-press-event", self._on_clicked)

        self.progressbar.set_size_request(100, 15)
        self.progressbar.set_ellipsize(Pango.EllipsizeMode.END)
        self.progressbar.set_text(text)
        self.progressbar.set_pulse_step(0.05)

        hbox.pack_end(eventbox, True, False, 0)
        hbox.pack_end(self.progressbar, False, False, 0)

        if ManagerProgressbar.__instances__:
            logging.info("hiding %s" % ManagerProgressbar.__instances__[-1])
            ManagerProgressbar.__instances__[-1].hide()

        self.show()
        if not self.cancellable:
            self.eventbox.props.sensitive = False

        self.pulsing = False
        self.finalized = False

        ManagerProgressbar.__instances__.append(self)

    def _on_enter(self, evbox, event):
        c = Gdk.Cursor.new(Gdk.CursorType.HAND2)
        self.Blueman.get_window().set_cursor(c)

    def _on_leave(self, evbox, event):
        self.Blueman.get_window().set_cursor(None)

    def _on_clicked(self, evbox, event):
        self.eventbox.props.sensitive = False
        self.emit("cancelled")

    def connect(self, *args):
        self._signals.append(super(ManagerProgressbar, self).connect(*args))

    def show(self):
        if not self.Blueman.Config["show-statusbar"]:
            self.Blueman.Builder.get_object("statusbar").props.visible = True

        self.progressbar.props.visible = True
        self.eventbox.props.visible = True
        self.button.props.visible = True

    def hide(self):
        self.Blueman.Stats.hbox.show_all()
        self.progressbar.props.visible = False
        self.eventbox.props.visible = False
        self.button.props.visible = False

    def message(self, msg, timeout=1500):
        self.stop()
        self.set_label(msg)
        self.set_cancellable(False)
        GLib.timeout_add(timeout, self.finalize)

    def finalize(self):
        if not self.finalized:
            self.hide()
            self.stop()
            self.Blueman.get_window().set_cursor(None)
            self.hbox.remove(self.eventbox)
            self.hbox.remove(self.progressbar)
            # self.hbox.remove(self.seperator)
            self.finalized = True

            if ManagerProgressbar.__instances__[-1] == self:
                ManagerProgressbar.__instances__.pop()
                # remove all finalized instances
                for inst in reversed(ManagerProgressbar.__instances__):
                    if inst.finalized:
                        ManagerProgressbar.__instances__.pop()
                    else:
                        # show last active progress bar
                        inst.show()
                        break

            if not ManagerProgressbar.__instances__:
                if not self.Blueman.Config["show-statusbar"]:
                    self.Blueman.Builder.get_object("statusbar").props.visible = False

            for sig in self._signals:
                self.disconnect(sig)
            self._signals = []

    def set_cancellable(self, b, hide=False):
        if b:
            self.eventbox.props.visible = True
            self.eventbox.props.sensitive = True
        else:
            if hide:
                self.eventbox.props.visible = False
            else:
                self.eventbox.props.sensitive = False

    def set_label(self, label):
        self.progressbar.props.text = label

    def fraction(self, frac):
        if not self.finalized:
            self.progressbar.set_fraction(frac)

    def started(self):
        return self.gsource is not None

    def start(self):
        def pulse():
            self.progressbar.pulse()
            return self.pulsing

        if not self.pulsing:
            self.pulsing = True
            GLib.timeout_add(1000 / 24, pulse)

    def stop(self):
        self.pulsing = False
        self.progressbar.set_fraction(0.0)
