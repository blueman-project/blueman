# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 


import gtk
import cairo
import gobject
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
		return (1-t)**2*p1 + 2*(1-t)*t*p2 + t**2*p3
		
	def get_value(self, input):
		return self.__b(input, self.start, self.curvature, self.end)

class AnimBase(gobject.GObject):
	__gsignals__ = {
		'animation-finished' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}
	
	def __init__(self, state=1.0):
		gobject.GObject.__init__(self)
		self._source = None
		self._state = state
		self.frozen = False
		self.fps = 24.0
		self.controller = LinearController()
		
	def set_controller(self, cls, *params):
		self.controller = cls(*params)

	def _do_transition(self):
		if abs(self._end-self._start) < 0.000001:
			return False
		
		self._state += self._step_size	
		
		if self._end-self._start < 0:
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
			gobject.source_remove(self._source)
		
		try:
			self._step_size = (end-start) / (self.fps * (duration/1000.0))
		except ZeroDivisionError:
			self._state = end

			return
			

		self._state_changed(self._state)
		self._source = gobject.timeout_add(int(1.0/self.fps*1000), self._do_transition)
			
		
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
		
		self.sig = self.tw.connect_after("expose-event", self.on_expose)
		
		self.row = gtk.TreeRowReference(tw.props.model, path)
		self.style = tw.rc_get_style()
		self.columns = None

	def unref(self):
		if self.sig != None:
			self.tw.disconnect(self.sig)
			self.sig = None			
			
	def get_iter(self):
		return self.tw.props.model.get_iter(self.row.get_path())
		
		
	def on_expose(self, widget, event):
		if self.frozen:
			return

		if not self.row.valid():
			self.tw.disconnect(self.sig)
			self.sig = None
			return
			
		path = self.row.get_path()
		
		area = gtk.gdk.Rectangle()
		
		cr = event.window.cairo_create()
		
		color = self.style.base[0]

		if not self.columns:
			columns = self.tw.get_columns()
		else:
			columns = self.columns
			
		for col in columns:
			cr.save()
			
			rect = self.tw.get_background_area(path, col)
			isected = event.area.intersect(rect)
			cr.rectangle(isected)
			cr.clip()

			cr.set_source_rgba((1.0/65535)*color.red, (1.0/65535)*color.green, (1.0/65535)*color.blue, 1.0-self.get_state())
			cr.set_operator(cairo.OPERATOR_OVER)
	 		cr.paint()
			
			cr.restore()


		
	def state_changed(self, state):
		self.tw.queue_draw()
		#print state
		
class TreeRowColorFade(TreeRowFade):
	def __init__(self, tw, path, color):
		TreeRowFade.__init__(self, tw, path, None)
		
		self.color = color
		
	def do_animation_finished(self):
		self.unref()
	
	def on_expose(self, widget, event):
		if self.frozen:
			return

		if not self.row.valid():
			self.tw.disconnect(self.sig)
			self.sig = None
			return
			
		path = self.row.get_path()
		
		area = gtk.gdk.Rectangle()
		
		cr = event.window.cairo_create()
		
		color = self.style.base[0]

		if not self.columns:
			columns = self.tw.get_columns()
		else:
			columns = self.columns
			
		for col in columns:
			cr.save()
			
			rect = self.tw.get_background_area(path, col)
			isected = event.area.intersect(rect)
			cr.rectangle(isected)
			cr.clip()

			cr.set_source_rgba((1.0/65535)*self.color.red, (1.0/65535)*self.color.green, (1.0/65535)*self.color.blue, 1.0-self.get_state())
			cr.set_operator(cairo.OPERATOR_OVER)
	 		cr.paint()
			
			cr.restore()	

class CellFade(AnimBase):
	def __init__(self, tw, path, columns=None):
		AnimBase.__init__(self, 1.0)
		self.tw = tw
		
		self.frozen = False
		self.sig = tw.connect_after("expose-event", self.on_expose)
		
		self.row = gtk.TreeRowReference(tw.props.model, path)
		self.selection = tw.get_selection()
		self.style = tw.rc_get_style()
		self.columns = []
		for i in columns:
			self.columns.append(self.tw.get_column(i))
			
	def unref(self):
		if self.sig != None:
			self.tw.disconnect(self.sig)
			self.sig = None		
			
	def get_iter(self):
		return self.tw.props.model.get_iter(self.row.get_path())
			
	def on_expose(self, widget, event):
		if self.frozen:
			return

		if not self.row.valid():
			self.tw.disconnect(self.sig)
			self.sig = None
			return
			
		path = self.row.get_path()
		
		area = gtk.gdk.Rectangle()
		
		cr = event.window.cairo_create()
		
		color = self.style.base[0]
			
		for col in self.columns:
			cr.save()
			
			bg_rect = self.tw.get_background_area(path, col)
			rect = self.tw.get_cell_area(path, col)
			rect.y = bg_rect.y
			rect.height = bg_rect.height
			
			isected = event.area.intersect(rect)
			cr.rectangle(isected)
			cr.clip()
			#print "expose", isected
			if not (isected.height == 0 or isected.height == 0):
				#print isected
				#print rect
				pixmap = gtk.gdk.Pixmap(event.window, isected.width, isected.height)
				gc = gtk.gdk.GC(event.window)
				pixmap.draw_drawable(gc, event.window, isected.x, isected.y, 0, 0, isected.width, isected.height)
			
				detail = "cell_even" if path[0] % 2 == 0 else "cell_odd"
				if self.tw.props.rules_hint:
					detail += "_ruled"
				
				selected = self.selection.get_selected()[1] and self.tw.props.model.get_path(self.selection.get_selected()[1]) == path
				
				self.tw.style.paint_flat_box(event.window, 
							     gtk.STATE_SELECTED if (selected) else gtk.STATE_NORMAL, 
							     0, 
							     isected, 
							     self.tw, 
							     detail, 
							     isected.x, 
							     isected.y, 
							     isected.width, 
							     isected.height)
			
				cr.set_source_pixmap(pixmap, isected.x, isected.y)
				cr.paint_with_alpha(self.get_state())
			
			cr.restore()
		
	def state_changed(self, state):
		self.tw.queue_draw()
		#print state
		
class WidgetFade(AnimBase):
	def __init__(self, widget, color):
		AnimBase.__init__(self, 1.0)
		
		self.widget = widget
		self.color = color
		
		self.sig = widget.connect_after("expose-event", self.on_expose)
		
	def on_expose(self, window, event):
		if not self.frozen:
			cr = event.window.cairo_create()

			rect = self.widget.allocation
			cr.rectangle(rect)
			cr.clip()		
		
			cr.set_source_rgba((1.0/65535)*self.color.red, (1.0/65535)*self.color.green, (1.0/65535)*self.color.blue, 1.0-self.get_state())
			cr.set_operator(cairo.OPERATOR_OVER)
		 	cr.paint()		

	
	def state_changed(self, state):
		self.widget.queue_draw()		
	
					

