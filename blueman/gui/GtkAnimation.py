from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Constants import *

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk

import cairo
from gi.repository import GObject
import weakref


class LinearController(object):
    def get_value(self, input):
        return input


class BezierController(LinearController):
    def __init__(self, curvature=0.5, start=0.0, end=1.0):
        self.curvature = curvature
        self.start = start
        self.end = end

    def __b(self, t, p1, p2, p3):
        return (1 - t) ** 2 * p1 + 2 * (1 - t) * t * p2 + t ** 2 * p3

    def get_value(self, input):
        return self.__b(input, self.start, self.curvature, self.end)


class AnimBase(GObject.GObject):
    __gsignals__ = {
    str('animation-finished'): (GObject.SignalFlags.RUN_LAST, None, ()),
    }

    def __init__(self, state=1.0):
        GObject.GObject.__init__(self)
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
            GObject.source_remove(self._source)

        try:
            self._step_size = (end - start) / (self.fps * (duration / 1000.0))
        except ZeroDivisionError:
            self._state = end

            return

        self._state_changed(self._state)
        self._source = GObject.timeout_add(int(1.0 / self.fps * 1000), self._do_transition)


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
        return self._source != None


class TreeRowFade(AnimBase):
    def __init__(self, tw, path, columns=None):
        AnimBase.__init__(self, 1.0)
        self.tw = tw

        self.sig = self.tw.connect_after("draw", self.on_expose)

        self.row = Gtk.TreeRowReference.new(tw.props.model, path)
        self.stylecontext = tw.get_style_context()
        self.columns = None

    def unref(self):
        if self.sig != None:
            self.tw.disconnect(self.sig)
            self.sig = None

    def get_iter(self):
        return self.tw.props.model.get_iter(self.row.get_path())


    def on_expose(self, widget, cr):
        if self.frozen:
            return

        if not self.row.valid():
            self.tw.disconnect(self.sig)
            self.sig = None
            return

        path = self.row.get_path()

        area = ()

        color = self.stylecontext.get_background_color(0)

        if not self.columns:
            columns = self.tw.get_columns()
        else:
            columns = self.columns

        for col in columns:
            rect = self.tw.get_background_area(path, col)
            Gdk.cairo_get_clip_rectangle(cr)
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
        TreeRowFade.__init__(self, tw, path, None)

        self.color = color

    def do_animation_finished(self):
        self.unref()

    def on_expose(self, widget, cr):
        if self.frozen:
            return

        if not self.row.valid():
            self.tw.disconnect(self.sig)
            self.sig = None
            return

        path = self.row.get_path()

        area = ()

        color = self.stylecontext.get_background_color(0)

        if not self.columns:
            columns = self.tw.get_columns()
        else:
            columns = self.columns

        for col in columns:
            rect = self.tw.get_background_area(path, col)
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.clip()

            cr.set_source_rgba(self.color.red, self.color.green, self.color.blue, 1.0 - self.get_state())
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.paint()


class CellFade(AnimBase):
    def __init__(self, tw, path, columns=None):
        AnimBase.__init__(self, 1.0)
        self.tw = tw

        self.frozen = False
        self.sig = tw.connect_after("draw", self.on_expose)
        self.row = Gtk.TreeRowReference.new(tw.props.model, path)
        self.selection = tw.get_selection()
        self.style = Gtk.rc_get_style(tw)
        self.stylecontext = tw.get_style_context()
        self.columns = []
        for i in columns:
            self.columns.append(self.tw.get_column(i))

    def unref(self):
        if self.sig != None:
            self.tw.disconnect(self.sig)
            self.sig = None

    def get_iter(self):
        return self.tw.props.model.get_iter(self.row.get_path())

    def on_expose(self, widget, cr):
        if self.frozen:
            return

        if not self.row.valid():
            self.tw.disconnect(self.sig)
            self.sig = None
            return

        path = self.row.get_path()

        area = ()

        color = self.stylecontext.get_background_color(0)

        for col in self.columns:
            bg_rect = self.tw.get_background_area(path, col)
            rect = self.tw.get_cell_area(path, col)
            rect.y = bg_rect.y
            rect.height = bg_rect.height

            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.clip()
            if not (rect.height == 0 or rect.height == 0):
                detail = "cell_even" if path[0] % 2 == 0 else "cell_odd"
                if self.tw.props.rules_hint:
                    detail += "_ruled"

                selected = self.selection.get_selected()[1] and self.tw.props.model.get_path(
                    self.selection.get_selected()[1]) == path

                Gtk.paint_flat_box(self.tw.get_style(),
                                   cr,
                                   Gtk.StateType.SELECTED if (selected) else Gtk.StateType.NORMAL,
                                   0,
                                   self.tw,
                                   detail,
                                   rect.x,
                                   rect.y,
                                   rect.width,
                                   rect.height)

                # FIXME pixmap got lost during port to gtk3
                #cr.set_source_pixmap(pixmap, rect.x, rect.y)
                cr.paint_with_alpha(self.get_state())

    def state_changed(self, state):
        self.tw.queue_draw()

    # print state


class WidgetFade(AnimBase):
    def __init__(self, widget, color):
        AnimBase.__init__(self, 1.0)

        self.widget = widget
        self.color = color

        self.sig = widget.connect_after("draw", self.on_expose)

    def on_expose(self, window, cr):
        if not self.frozen:
            rect = self.widget.get_allocation()
            cr.rectangle(rect.x, rect.y, rect.width, rect.height)
            cr.clip()
            cr.set_source_rgba(self.color.red, self.color.green, self.color.blue, self.color.alpha - self.get_state())
            cr.set_operator(cairo.OPERATOR_OVER)
            cr.paint()


    def state_changed(self, state):
        self.widget.queue_draw()
