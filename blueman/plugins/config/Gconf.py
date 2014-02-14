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
from gi.repository import GConf
import os
import subprocess

BLUEMAN_PATH = "/apps/blueman"

class Gconf(ConfigPlugin):
	__priority__ = 0
	__plugin__ = "GConf"
	
	def on_load(self, section):
		self.section = section
		if self.section != "":
			self.section = "/" + self.section
		
		self.client = GConf.Client.get_default ()
		
		self.client.add_dir(BLUEMAN_PATH + self.section, GConf.ClientPreloadType.PRELOAD_ONELEVEL)
		self.client.connect("value_changed", self.value_changed)

	# convert a GConfValue to python native value
	def gval2pyval(self, val):
		if val.type == GConf.ValueType.STRING:
			return val.get_string()
		elif val.type == GConf.ValueType.FLOAT:
			return val.get_float()
		elif val.type == GConf.ValueType.INT:
			return val.get_int()
		elif val.type == GConf.ValueType.BOOL:
			return val.get_bool()
		elif val.type == GConf.ValueType.LIST:
			x = []
			for item in val.get_list():
				x.append(self.gval2pyval(item))
			return x
		else:
			raise AttributeError("Cant get this type from GConf: %s" % str(val.type))
	
	def value_changed(self, client, key, value):
		if os.path.dirname(key) == BLUEMAN_PATH + self.section:
			name = os.path.basename(key)
			self.emit("property-changed", name, self.get(name))		
	
	def _set_gconf_list(self, key, values):
		gconf_value = '[%s]' % ','.join(values)
		subprocess.check_output(["gconftool-2", "--set", "--type=list", "--list-type=string", key, gconf_value])
	
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
			func = self._set_gconf_list
		else:
			raise AttributeError("Cant set this type in GConf: %s" % str(type(value)))
		
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
