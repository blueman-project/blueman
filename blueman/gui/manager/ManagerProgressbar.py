# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
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
import pango
import gobject
import gtk
import gtk.gdk
from blueman.Functions import get_icon

class ManagerProgressbar(gobject.GObject):

	__gsignals__ = {
		'cancelled' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}
	def __init__(self, blueman, cancellable=True, text="Connecting"):
		def on_enter(evbox, event):
			c = gtk.gdk.Cursor( gtk.gdk.HAND2)
			self.window.window.set_cursor(c)
		
		def on_leave(evbox, event):
			self.window.window.set_cursor(None)
			
		def on_clicked(evbox, event):
			self.eventbox.props.sensitive = False
			self.emit("cancelled")
		
		gobject.GObject.__init__(self)
		
		self.cancellable = cancellable
		
		self.hbox = hbox = blueman.Builder.get_object("statusbar1_hb")
		
		self.progressbar = gtk.ProgressBar()
		self.seperator = gtk.VSeparator()
		

		self.button = gtk.image_new_from_pixbuf(get_icon("gtk-stop", 16))
	
		self.eventbox = eventbox = gtk.EventBox()
		eventbox.add(self.button)
		eventbox.connect("enter-notify-event", on_enter)
		eventbox.connect("leave-notify-event", on_leave)
		eventbox.connect("button-press-event", on_clicked)

		
		self.progressbar.set_size_request(100, 15)
		self.progressbar.set_ellipsize(pango.ELLIPSIZE_END)
		self.progressbar.set_text(text)
		self.progressbar.set_pulse_step(0.05)
		
		self.window = blueman.Builder.get_object("window")

		hbox.pack_end(eventbox, True, False)
		hbox.pack_end(self.progressbar, False, False)
		hbox.pack_end(self.seperator, False, False)
		hbox.show_all()
		
		if not self.cancellable:
			self.eventbox.props.visible = False
		
		self.gsource = None
		self.finalized = False
		
	def finalize(self):
		if not self.finalized:
			self.stop()

			self.hbox.remove(self.eventbox)
			self.hbox.remove(self.progressbar)
			self.hbox.remove(self.seperator)
			self.finalized = True
		
		
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
	
	def start(self):
		def pulse():
			self.progressbar.pulse()
			return True
		
		self.gsource = gobject.timeout_add(1000/24, pulse)
	
	def stop(self):
		if self.gsource != None:
			gobject.source_remove(self.gsource)
		self.progressbar.set_fraction(0.0)
