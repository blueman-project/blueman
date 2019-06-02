# coding=utf-8
import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib


class LinearController(object):
    def get_value(self, inpt):
        return inpt


class BezierController(LinearController):
    def __init__(self, curvature=0.5, start=0.0, end=1.0):
        self.curvature = curvature
        self.start = start
        self.end = end

    def __b(self, t, p1, p2, p3):
        return (1 - t) ** 2 * p1 + 2 * (1 - t) * t * p2 + t ** 2 * p3

    def get_value(self, inpt):
        return self.__b(inpt, self.start, self.curvature, self.end)


class AnimBase(GObject.GObject):
    __gsignals__ = {
        'animation-finished': (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, state=1.0):
        super().__init__()
        self._source = None
        self._state = state
        self.frozen = False
        self.fps = 24.0
        self.controller = LinearController()

    def set_controller(self, cls, *params):
        self.controller = cls(*params)

    def _do_transition(self):
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

    def thaw(self):
        self.frozen = False
        self.on_frozen(self.frozen)

    def freeze(self):
        self.frozen = True
        self.on_frozen(self.frozen)

    def on_frozen(self, is_frozen):
        pass

    def animate(self, start=1.0, end=0.0, duration=1000):
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

    def _state_changed(self, state):
        self.state_changed(self.controller.get_value(state))

    def state_changed(self, state):
        pass

    def get_state(self):
        return self._state

    def set_state(self, state):
        self._state = state
        self._state_changed(state)

    def is_animating(self):
        return self._source is not None


class TreeRowFade(AnimBase):
    def __init__(self, tw, path, columns=None):
        super().__init__(1.0)
        self.tw = tw

        self.sig = self.tw.connect_after("draw", self.on_draw)

        self.row = Gtk.TreeRowReference.new(tw.props.model, path)
        self.stylecontext = tw.get_style_context()
        self.columns = columns

    def unref(self):
        if self.sig is not None:
            self.tw.disconnect(self.sig)
            self.sig = None

    def get_iter(self):
        return self.tw.props.model.get_iter(self.row.get_path())

    def on_draw(self, widget, cr):
        if self.frozen:
            return

        if not self.row.valid():
            self.tw.disconnect(self.sig)
            self.sig = None
            return

        path = self.row.get_path()

        color = self.stylecontext.get_background_color(Gtk.StateFlags.NORMAL)

        if not self.columns:
            self.columns = self.tw.get_columns()

        for col in self.columns:
            rect = self.tw.get_background_area(path, col)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

        cr.clip()

        cr.set_source_rgba(color.red, color.green, color.blue, 1.0 - self.get_state())
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.paint()

    def state_changed(self, state):
        self.tw.queue_draw()

    # print state


class TreeRowColorFade(TreeRowFade):
    def __init__(self, tw, path, color):
        super().__init__(tw, path, None)

        self.color = color

    def do_animation_finished(self):
        self.unref()

    def on_draw(self, widget, cr):
        if self.frozen:
            return

        if not self.row.valid():
            self.tw.disconnect(self.sig)
            self.sig = None
            return

        path = self.row.get_path()

        if not self.columns:
            self.columns = self.tw.get_columns()

        for col in self.columns:
            rect = self.tw.get_background_area(path, col)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

        cr.clip()

        cr.set_source_rgba(self.color.red, self.color.green, self.color.blue, 1.0 - self.get_state())
        cr.set_operator(cairo.OPERATOR_OVER)
        cr.paint()


class CellFade(AnimBase):
    def __init__(self, tw, path, columns=None):
        super().__init__(1.0)
        self.tw = tw

        self.frozen = False
        self.sig = tw.connect_after("draw", self.on_draw)
        self.row = Gtk.TreeRowReference.new(tw.props.model, path)
        self.selection = tw.get_selection()
        self.columns = []
        for i in columns:
            self.columns.append(self.tw.get_column(i))

    def unref(self):
        if self.sig is not None:
            self.tw.disconnect(self.sig)
            self.sig = None

    def get_iter(self):
        return self.tw.props.model.get_iter(self.row.get_path())

    def on_draw(self, widget, cr):
        if self.frozen:
            return

        if not self.row.valid():
            self.tw.disconnect(self.sig)
            self.sig = None
            return

        path = self.row.get_path()

        # FIXME Use Gtk.render_background to render background.
        # However it does not use the correct colors/gradient.
        for col in self.columns:
            bg_rect = self.tw.get_background_area(path, col)
            rect = self.tw.get_cell_area(path, col)
            rect.y = bg_rect.y
            rect.height = bg_rect.height

            cr.rectangle(rect.x, rect.y, rect.width, rect.height)

        cr.clip()

        selected = self.selection.get_selected()[1] and \
            self.tw.props.model.get_path(self.selection.get_selected()[1]) == path

        stylecontext = self.tw.get_style_context()

        if selected:
            bg_color = stylecontext.get_background_color(Gtk.StateFlags.SELECTED)
        else:
            bg_color = stylecontext.get_background_color(Gtk.StateFlags.NORMAL)

        cr.set_source_rgb(bg_color.red, bg_color.green, bg_color.blue)
        cr.paint_with_alpha(1.0 - self.get_state())

    def state_changed(self, state):
        self.tw.queue_draw()

    # print state


class WidgetFade(AnimBase):
    def __init__(self, widget, color):
        super().__init__(1.0)

        self.widget = widget
        self.color = color

        self.sig = widget.connect_after("draw", self.on_draw)

    def on_draw(self, widget, cr):
        if not self.frozen:
            cr.set_source_rgba(self.color.red, self.color.green, self.color.blue, self.color.alpha - self.get_state())
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.paint()

    def state_changed(self, state):
        self.widget.queue_draw()
