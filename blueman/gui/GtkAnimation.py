from typing import List, Optional, Collection, Iterable, TYPE_CHECKING

import cairo
import gi

from blueman.bluemantyping import GSignals

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib


if TYPE_CHECKING:
    from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList


class AnimBase(GObject.GObject):
    __gsignals__: GSignals = {
        'animation-finished': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, state: float = 1.0) -> None:
        super().__init__()
        self._source: Optional[int] = None
        self._state = state
        self.frozen = False
        self.fps = 24.0

    def _do_transition(self) -> bool:
        if abs(self._end - self._start) < 0.000001:
            return False

        self._state += self._step_size

        if self._end - self._start < 0:
            if self._state <= self._end:
                self._state = self._end
                self._state_changed(self._state)
                self._source = None
                self.emit("animation-finished")
                return False
        else:
            if self._state >= self._end:
                self._state = self._end
                self._state_changed(self._state)
                self._source = None
                self.emit("animation-finished")
                return False

        self._state_changed(self._state)
        return True

    def thaw(self) -> None:
        self.frozen = False

    def freeze(self) -> None:
        self.frozen = True

    def animate(self, start: float = 1.0, end: float = 0.0, duration: int = 1000) -> None:
        if self.frozen:
            self.emit("animation-finished")
            return

        self._state = start
        self._start = start
        self._end = end
        self._duration = duration

        if self._source:
            GLib.source_remove(self._source)

        try:
            self._step_size = (end - start) / (self.fps * (duration / 1000.0))
        except ZeroDivisionError:
            self._state = end

            return

        self._state_changed(self._state)
        self._source = GLib.timeout_add(int(1.0 / self.fps * 1000), self._do_transition)

    def _state_changed(self, state: float) -> None:
        self.state_changed(state)

    def state_changed(self, state: float) -> None:
        pass

    def get_state(self) -> float:
        return self._state

    def set_state(self, state: float) -> None:
        self._state = state
        self._state_changed(state)

    def is_animating(self) -> bool:
        return self._source is not None


class TreeRowFade(AnimBase):
    def __init__(self, tw: "ManagerDeviceList",
                 path: Gtk.TreePath,
                 columns: Optional[Collection[Gtk.TreeViewColumn]] = None) -> None:
        super().__init__(1.0)
        self.tw = tw
        assert self.tw.liststore is not None

        self.sig: Optional[int] = self.tw.connect_after("draw", self.on_draw)

        self.row = Gtk.TreeRowReference.new(self.tw.liststore, path)
        self.stylecontext = tw.get_style_context()
        self.columns = columns

    def unref(self) -> None:
        if self.sig is not None:
            self.tw.disconnect(self.sig)
            self.sig = None

    def on_draw(self, widget: Gtk.Widget, cr: cairo.Context) -> bool:
        if self.frozen:
            return False

        if not self.row.valid():
            if self.sig is not None:
                self.tw.disconnect(self.sig)
                self.sig = None
            return False

        path = self.row.get_path()
        if path is None:
            return False

        path = self.tw.filter.convert_child_path_to_path(path)
        if path is None:
            return False

        color = self.stylecontext.get_background_color(Gtk.StateFlags.NORMAL)

        if not self.columns:
            self.columns = self.tw.get_columns()
        assert self.columns is not None

        for col in self.columns:
            rect = self.tw.get_background_area(path, col)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

        cr.clip()

        cr.set_source_rgba(color.red, color.green, color.blue, 1.0 - self.get_state())
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.paint()

        return False

    def state_changed(self, state: float) -> None:
        self.tw.queue_draw()


class CellFade(AnimBase):
    def __init__(self, tw: "ManagerDeviceList", path: Gtk.TreePath, columns: Iterable[int]) -> None:
        super().__init__(1.0)
        self.tw = tw
        assert self.tw.liststore is not None

        self.frozen = False
        self.sig: Optional[int] = tw.connect_after("draw", self.on_draw)
        self.row = Gtk.TreeRowReference.new(self.tw.liststore, path)
        self.selection = tw.get_selection()
        self.columns: List[Optional[Gtk.TreeViewColumn]] = []
        for i in columns:
            self.columns.append(self.tw.get_column(i))

    def unref(self) -> None:
        if self.sig is not None:
            self.tw.disconnect(self.sig)
            self.sig = None

    def on_draw(self, _widget: Gtk.Widget, cr: cairo.Context) -> bool:
        if self.frozen:
            return False

        if not self.row.valid():
            if self.sig is not None:
                self.tw.disconnect(self.sig)
                self.sig = None

        assert self.tw.liststore is not None
        path = self.row.get_path()
        if path is None:
            return False

        path = self.tw.filter.convert_child_path_to_path(path)
        if path is None:
            return False

        # FIXME Use Gtk.render_background to render background.
        # However it does not use the correct colors/gradient.
        for col in self.columns:
            bg_rect = self.tw.get_background_area(path, col)
            rect = self.tw.get_cell_area(path, col)
            rect.y = bg_rect.y
            rect.height = bg_rect.height

            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

        cr.clip()

        maybe_selected = self.tw.selected()
        if maybe_selected is not None:
            selected = self.tw.liststore.get_path(maybe_selected) == path
        else:
            selected = False

        stylecontext = self.tw.get_style_context()

        if selected:
            bg_color = stylecontext.get_background_color(Gtk.StateFlags.SELECTED)
        else:
            bg_color = stylecontext.get_background_color(Gtk.StateFlags.NORMAL)

        cr.set_source_rgb(bg_color.red, bg_color.green, bg_color.blue)
        cr.paint_with_alpha(1.0 - self.get_state())

        return False

    def state_changed(self, state: float) -> None:
        self.tw.queue_draw()


class WidgetFade(AnimBase):
    def __init__(self, widget: Gtk.Widget, color: Gdk.RGBA) -> None:
        super().__init__(1.0)

        self.widget = widget
        self.color = color

        self.sig = widget.connect_after("draw", self.on_draw)

    def on_draw(self, _widget: Gtk.Widget, cr: cairo.Context) -> bool:
        if not self.frozen:
            cr.set_source_rgba(self.color.red, self.color.green, self.color.blue, self.color.alpha - self.get_state())
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.paint()
        return False

    def state_changed(self, state: float) -> None:
        self.widget.queue_draw()
