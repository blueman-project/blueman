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
from blueman.functions import get_icon

class manager_progressbar(gobject.GObject):

	__gsignals__ = {
		'cancelled' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
	}
	def __init__(self, blueman):
		def on_enter(evbox, event):
			c = gtk.gdk.Cursor( gtk.gdk.HAND2)
			self.window.window.set_cursor(c)
		
		def on_leave(evbox, event):
			self.window.window.set_cursor(None)
			
		def on_clicked(evbox, event):
			self.button.props.sensitive = False
			self.emit("cancelled")
		
		gobject.GObject.__init__(self)
		hbox = blueman.Builder.get_object("statusbar_hb")
		
		self.progressbar = gtk.ProgressBar()
		self.seperator = gtk.VSeparator()
		self.button = gtk.image_new_from_pixbuf(get_icon("gtk-stop", 16))
		
		eventbox = gtk.EventBox()
		eventbox.add(self.button)
		eventbox.connect("enter-notify-event", on_enter)
		eventbox.connect("leave-notify-event", on_leave)
		eventbox.connect("button-press-event", on_clicked)

		
		self.progressbar.set_size_request(100, 15)
		self.progressbar.set_ellipsize(pango.ELLIPSIZE_END)
		self.progressbar.set_text("Connecting")
		
		self.window = blueman.Builder.get_object("window")

		
		hbox.pack_end(eventbox, False, False)
		hbox.pack_end(self.progressbar, False, False)
		hbox.pack_end(self.seperator, False, False)
		hbox.show_all()
		
		
		
	
	def start(self):
		pass
	
	def stop(self):
		pass
