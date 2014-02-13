# Copyright (C) 2009 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2009 Tadas Dailyda <tadas at dailyda dot com>
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

from gi.repository import GObject
import weakref

class ConfigPlugin(GObject.GObject):
	__plugin__ = None
	__priority__ = None
	
	__gsignals__ = {
		#@param: self key value
		'property-changed' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
	}
	
	class props:
		def __init__(self, Config):
			self.__dict__["Config"] = Config
		
		def __setattr__(self, key, value):
			self.__dict__["Config"]().set(key, value)
				
		def __getattr__(self, key):
			return self.__dict__["Config"]().get(key)

	def __init__(self, section=""):
		GObject.GObject.__init__(self)

		self.props = ConfigPlugin.props(weakref.ref(self))
		
		self.on_load(section)
	
	#virtual functions
	def on_load(self, section):
		pass
		
	def get(self, key):
		pass
		
	def set(self, key, val):
		pass
		
	def list_dirs(self):
		pass
	

