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
import math

class PixbufTable:
	def __init__(self, percol=2, spacingx=1, spacingy=1, size=24):
		self.percol = percol
		self.spacingx=spacingx
		self.spacingy=spacingy
		self.size=size
		
		self.cols = 0
		
		self.pixbuffs = {}
		
		self.recalc()


	def recalc(self):
		if len(self.pixbuffs) == 0:
			self.total_width = 0
			self.total_height = 0
			self.rows = 0
			self.cols = 0
			return
		
		self.cols = int(math.ceil(float(len(self.pixbuffs)) / self.percol))


		spacing_width = (self.cols -1) * self.spacingx

		

		if len(self.pixbuffs) >= self.percol:
			self.rows = self.percol
		else:
			self.rows = len(self.pixbuffs)
			
		spacing_height = (self.rows -1) * self.spacingy
			
		self.total_width = self.cols * self.size + spacing_width
		self.total_height = self.rows * self.size + spacing_height		
	
	def get(self):
		return self.pixbuffs
		
	def set(self, name, pixbuf):
		if pixbuf != None:
			self.pixbuffs[name] = pixbuf
		else:
			if name in self.pixbuffs:
				del self.pixbuffs[name]
		self.recalc()


