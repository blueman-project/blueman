from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from blueman.Functions import get_icon, dprint
from blueman.main.SignalTracker import SignalTracker


class ManagerProgressbar(GObject.GObject):
    __gsignals__ = {
    str('cancelled'): (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    __instances__ = []

    def __init__(self, blueman, cancellable=True, text=_("Connecting")):
        def on_enter(evbox, event):
            c = Gdk.Cursor.new(Gdk.CursorType.HAND2)
            self.window.get_window().set_cursor(c)

        def on_leave(evbox, event):
            self.window.get_window().set_cursor(None)

        def on_clicked(evbox, event):
            self.eventbox.props.sensitive = False
            self.emit("cancelled")

        GObject.GObject.__init__(self)
        self.Blueman = blueman

        self.cancellable = cancellable

        self.hbox = hbox = blueman.Builder.get_object("statusbar1")

        self.progressbar = Gtk.ProgressBar()

        self.signals = SignalTracker()

        self.button = Gtk.Image.new_from_pixbuf(get_icon("process-stop", 16))

        self.eventbox = eventbox = Gtk.EventBox()
        eventbox.add(self.button)
        eventbox.props.tooltip_text = _("Cancel Operation")
        self.signals.Handle(eventbox, "enter-notify-event", on_enter)
        self.signals.Handle(eventbox, "leave-notify-event", on_leave)
        self.signals.Handle(eventbox, "button-press-event", on_clicked)

        self.progressbar.set_size_request(100, 15)
        self.progressbar.set_ellipsize(Pango.EllipsizeMode.END)
        self.progressbar.set_text(text)
        self.progressbar.set_pulse_step(0.05)

        self.window = blueman.Builder.get_object("window")

        hbox.pack_end(eventbox, True, False, 0)
        hbox.pack_end(self.progressbar, False, False, 0)

        if ManagerProgressbar.__instances__ != []:
            dprint("hiding", ManagerProgressbar.__instances__[-1])
            ManagerProgressbar.__instances__[-1].hide()

        self.show()
        if not self.cancellable:
            self.eventbox.props.sensitive = False

        self.gsource = None
        self.finalized = False

        ManagerProgressbar.__instances__.append(self)

    def connect(self, *args):
        self.signals.Handle("gobject", super(ManagerProgressbar, self), *args)

    def show(self):
        if not self.Blueman.Config["show-statusbar"]:
            self.Blueman.Builder.get_object("statusbar").props.visible = True


        # if self.Blueman.Stats.hbox.size_request()[0] + self.progressbar.size_request()[0] + 16 > self.Blueman.window.get_size()[0]:
        #	self.Blueman.Stats.hbox.hide_all()


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
        GObject.timeout_add(timeout, self.finalize)


    def finalize(self):
        if not self.finalized:
            self.hide()
            self.stop()
            Gdk.Window.set_cursor(self.window.get_window(), None)
            self.hbox.remove(self.eventbox)
            self.hbox.remove(self.progressbar)
            # self.hbox.remove(self.seperator)
            self.finalized = True

            if ManagerProgressbar.__instances__[-1] == self:
                ManagerProgressbar.__instances__.pop()
                #remove all finalized instances
                for inst in reversed(ManagerProgressbar.__instances__):
                    if inst.finalized:
                        ManagerProgressbar.__instances__.pop()
                    else:
                        #show last active progress bar
                        inst.show()
                        break

            if ManagerProgressbar.__instances__ == []:
                if not self.Blueman.Config["show-statusbar"]:
                    self.Blueman.Builder.get_object("statusbar").props.visible = False

            self.signals.DisconnectAll()


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
        return self.gsource != None

    def start(self):
        def pulse():
            self.progressbar.pulse()
            return True

        if not self.gsource:
            self.gsource = GObject.timeout_add(1000 / 24, pulse)

    def stop(self):
        if self.gsource != None:
            GObject.source_remove(self.gsource)
        self.progressbar.set_fraction(0.0)
