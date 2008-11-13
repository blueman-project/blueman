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
import gconf
import gobject
import os.path

BLUEMAN_PATH = "/apps/blueman"

class Config(gobject.GObject):
	__gsignals__ = {
		#@param: self key value
		'property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
	}
	
	class props:
		def __init__(self, Config):
			self.Config = Config
		def __setattr__(self, key, value):
			if key == "Config" or key in self.__dict__:
				self.__dict__[key] = value
			else:
				print "setting gconf", key, value
				func = None
			
				if type(value) == str:
					func = self.Config.client.set_string
				elif type(value) == int:
					func = self.Config.client.set_int
				elif type(value) == bool:
					func = self.Config.client.set_bool
				elif type(value) == float:
					func = self.Config.client.set_float
				else:
					raise AttributeError("Cant set this type in gconf")
				
				func(BLUEMAN_PATH + self.Config.subdir + "/" + key, value)
				
		def __getattr__(self, key):
			if key == "Config" or key in self.__dict__:
				return self.__dict__[key]
			else:
				return self.Config.get_value(key)
				
	def get_value(self, key):
		val = self.client.get(BLUEMAN_PATH + self.subdir + "/" + key)
		if val != None:
			if val.type == gconf.VALUE_STRING:
				return val.get_string()
			elif val.type == gconf.VALUE_FLOAT:
				return val.get_float()
			elif val.type == gconf.VALUE_INT:
				return val.get_int()
			elif val.type == gconf.VALUE_BOOL:
				return val.get_bool()
			else:
				raise AttributeError("Cant get this type from gconf")
		else:
			return None

	
	def value_changed(self, client, key, value):
		name = os.path.basename(key)
		self.emit("property-changed", name, self.get_value(name))
	
	def __init__(self, subdir=""):
		self.subdir = subdir
		if self.subdir != "":
			self.subdir = "/" + self.subdir 
		gobject.GObject.__init__(self)
		
		self.client = gconf.client_get_default ()
		
		self.props = Config.props(self)
		
		self.client.add_dir(BLUEMAN_PATH + self.subdir, gconf.CLIENT_PRELOAD_RECURSIVE)
		self.client.connect("value_changed", self.value_changed)


