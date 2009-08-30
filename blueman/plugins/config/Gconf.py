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

from blueman.plugins.ConfigPlugin import ConfigPlugin
import gconf
import os

BLUEMAN_PATH = "/apps/blueman"

class Gconf(ConfigPlugin):
	__priority__ = 0
	__plugin__ = "gconf"
	
	def on_load(self, section):
		self.section = section
		if self.section != "":
			self.section = "/" + self.section
		
		self.client = gconf.client_get_default ()
		
		self.client.add_dir(BLUEMAN_PATH + self.section, gconf.CLIENT_PRELOAD_ONELEVEL)
		self.client.connect("value_changed", self.value_changed)

	# convert a GConfValue to python native value
	def gval2pyval(self, val):
		if val.type == gconf.VALUE_STRING:
			return val.get_string()
		elif val.type == gconf.VALUE_FLOAT:
			return val.get_float()
		elif val.type == gconf.VALUE_INT:
			return val.get_int()
		elif val.type == gconf.VALUE_BOOL:
			return val.get_bool()
		elif val.type == gconf.VALUE_LIST:
			x = []
			for item in val.get_list():
				x.append(self.gval2pyval(item))
			return x
		else:
			raise AttributeError("Cant get this type from gconf")
	
	def value_changed(self, client, key, value):
		if os.path.dirname(key) == BLUEMAN_PATH + self.section:
			name = os.path.basename(key)
			self.emit("property-changed", name, self.get(name))		
	
	def set(self, key, value):
		func = None
	
		if type(value) == str:
			func = self.client.set_string
		elif type(value) == int:
			func = self.client.set_int
		elif type(value) == bool:
			func = self.client.set_bool
		elif type(value) == float:
			func = self.client.set_float
		elif type(value) == list:
			def x(key, val):
				self.client.set_list(key, gconf.VALUE_STRING, val)
			func = x
		else:
			raise AttributeError("Cant set this type in gconf")
		
		func(BLUEMAN_PATH + self.section + "/" + key, value)
		
	def get(self, key):
		val = self.client.get(BLUEMAN_PATH + self.section + "/" + key)
		if val != None:
			return self.gval2pyval(val)
		else:
			return None
			
	def list_dirs(self):
		rets = self.client.all_dirs(BLUEMAN_PATH + self.section)
		l = []
		for r in rets:
			l.append(r.replace(BLUEMAN_PATH + "/", ""))
		return l
