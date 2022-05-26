from gettext import gettext as _
import logging
from typing import List, TYPE_CHECKING, Callable

import gi

from blueman.bluemantyping import GSignals

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Pango
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerProgressbar(GObject.GObject):
    __gsignals__: GSignals = {
        'cancelled': (GObject.SignalFlags.RUN_LAST, None, ()),
    }
    __instances__: List["ManagerProgressbar"] = []

    def __init__(self, blueman: "Blueman", cancellable: bool = True, text: str = _("Connecting")) -> None:
        super().__init__()
        self.Blueman = blueman

        self.cancellable = cancellable

        self.hbox = hbox = blueman.builder.get_widget("status_data", Gtk.Box)

        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_name("ManagerProgressbar")

        self._signals: List[int] = []

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
        self.progressbar.set_show_text(True)
        self.progressbar.set_pulse_step(0.05)

        hbox.pack_end(eventbox, True, False, 5)
        hbox.pack_end(self.progressbar, False, False, 5)

        if ManagerProgressbar.__instances__:
            logging.info(f"hiding {ManagerProgressbar.__instances__[-1]}")
            ManagerProgressbar.__instances__[-1].hide()

        self.show()
        if not self.cancellable:
            self.eventbox.props.sensitive = False

        self.pulsing = False
        self.finalized = False

        ManagerProgressbar.__instances__.append(self)

    def _get_window(self) -> Gdk.Window:
        assert self.Blueman.window is not None
        window = self.Blueman.window.get_window()
        assert window is not None
        return window

    def _on_enter(self, _evbox: Gtk.EventBox, _event: Gdk.Event) -> bool:
        c = Gdk.Cursor.new(Gdk.CursorType.HAND2)
        self._get_window().set_cursor(c)
        return False

    def _on_leave(self, _evbox: Gtk.EventBox, _event: Gdk.Event) -> bool:
        assert self.Blueman.window is not None
        self._get_window().set_cursor(None)
        return False

    def _on_clicked(self, _evbox: Gtk.EventBox, _event: Gdk.Event) -> bool:
        self.eventbox.props.sensitive = False
        self.emit("cancelled")
        return False

    def connect(self, signal: str, callback: Callable[..., None], *args: object) -> int:
        handler_id: int = super().connect(signal, callback, *args)
        self._signals.append(handler_id)
        return handler_id

    def show(self) -> None:
        if not self.Blueman.Config["show-statusbar"]:
            statusbar = self.Blueman.builder.get_widget("statusbar", Gtk.Box)
            statusbar.props.visible = True

        self.progressbar.props.visible = True
        self.eventbox.props.visible = True
        self.button.props.visible = True

    def hide(self) -> None:
        self.Blueman.Stats.hbox.show_all()
        self.progressbar.props.visible = False
        self.eventbox.props.visible = False
        self.button.props.visible = False

    def message(self, msg: str, timeout: int = 1500) -> None:
        self.stop()
        self.set_label(msg)
        self.set_cancellable(False)
        GLib.timeout_add(timeout, self.finalize)

    def finalize(self) -> bool:
        if not self.finalized:
            self.hide()
            self.stop()
            self._get_window().set_cursor(None)
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
                    statusbar = self.Blueman.builder.get_widget("statusbar", Gtk.Box)
                    statusbar.props.visible = False

            for sig in self._signals:
                if self.handler_is_connected(sig):
                    self.disconnect(sig)
            self._signals = []
        return False

    def set_cancellable(self, b: bool, hide: bool = False) -> None:
        if b:
            self.eventbox.props.visible = True
            self.eventbox.props.sensitive = True
        else:
            if hide:
                self.eventbox.props.visible = False
            else:
                self.eventbox.props.sensitive = False

    def set_label(self, label: str) -> None:
        self.progressbar.props.text = label

    def fraction(self, frac: float) -> None:
        if not self.finalized:
            self.progressbar.set_fraction(frac)

    def started(self) -> bool:
        return self.pulsing

    def start(self) -> None:
        def pulse() -> bool:
            self.progressbar.pulse()
            return self.pulsing

        if not self.pulsing:
            self.pulsing = True
            GLib.timeout_add(41, pulse)

    def stop(self) -> None:
        self.pulsing = False
        self.progressbar.set_fraction(0.0)
