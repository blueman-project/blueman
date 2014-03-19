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

from gi.repository import Gtk
from gi.repository import GObject


class CellRendererPixbufTable(Gtk.CellRenderer):
	__gproperties__ = {
		"pixbuffs": (GObject.TYPE_PYOBJECT, "pixbuf", "pixbuf", GObject.PARAM_READWRITE)

	}

	def __init__(self):
		self.__gobject_init__()


		self.set_property("yalign", 0.5)
		self.set_property("xalign", 0.5)

	
	def do_set_property(self, pspec, value):
			setattr(self, pspec.name, value)

	def do_get_property(self, pspec):
			return getattr(self, pspec.name)

	def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
		if not self.pixbuffs or self.pixbuffs.cols == 0:
			return


		pix_rect = ()
		pix_rect.x, pix_rect.y, pix_rect.width, pix_rect.height = self.on_get_size(widget, cell_area)

		
		pix_rect.x += cell_area.x
		pix_rect.y += cell_area.y
		pix_rect.width  -= 2 * self.get_property("xpad") + (self.pixbuffs.total_width - self.pixbuffs.size)
		pix_rect.height -= 2 * self.get_property("ypad") + (self.pixbuffs.total_height - self.pixbuffs.size)

		
		row = 0
		col = 0
		
	
		for k,v in self.pixbuffs.get().iteritems():
			#print rows
			if row == self.pixbuffs.rows:
				y_space = 0
				row=0
				col+=1

			else:
				y_space = self.pixbuffs.spacingy
				
			if col == 0 or col == self.pixbuffs.cols:
				x_space = 0
			else:
				x_space = self.pixbuffs.spacingx
		
				

			draw_rect = cell_area.intersect(pix_rect)
			draw_rect = expose_area.intersect(draw_rect)
			
			
			if self.pixbuffs.cols > 2:
				z = self.pixbuffs.size*(self.pixbuffs.cols-1)
			else:
				z = 0
			
			h = v.get_height()
			w = v.get_width()
			#if w > h:
			#	x = 
				
			
			
			window.draw_pixbuf(
					widget.style.black_gc, 
					v, 
					draw_rect.x - pix_rect.x, #source x
					draw_rect.y - pix_rect.y, #source y
					int(draw_rect.x + self.pixbuffs.size * col + x_space*col + (cell_area.width-self.pixbuffs.total_width) * self.get_property("xalign") + (h - w)/2), #dest x
					int(draw_rect.y + self.pixbuffs.size * row + y_space*row + (cell_area.height-self.pixbuffs.total_height) * self.get_property("yalign")), #dest y
					-1,
					-1,
					Gdk.RGB_DITHER_NONE,
					0,
					0
					)
			
			row += 1


	def on_get_size(self, widget, cell_area):
		if not self.pixbuffs or self.pixbuffs.cols == 0:
			return 0, 0, 0, 0


		calc_width  = self.get_property("xpad") * 2 + self.pixbuffs.size + (self.pixbuffs.total_width - self.pixbuffs.size)
		calc_height = self.get_property("ypad") * 2 + self.pixbuffs.size + (self.pixbuffs.total_height - self.pixbuffs.size)
		x_offset = 0
		y_offset = 0
		
		return x_offset, y_offset, calc_width, calc_height

GObject.type_register(CellRendererPixbufTable)
