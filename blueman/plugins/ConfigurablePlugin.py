# Copyright (C) 2010 Valmantas Paliksa <walmis at balticum-tv dot lt>
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
from blueman.plugins.BasePlugin import BasePlugin
from gi.repository import Gio

class ConfigurablePlugin(BasePlugin):
	
	__options__ = {}
	
	@classmethod
	def is_configurable(cls):
		res = map(lambda x: (len(x) > 2), cls.__options__.values())
		return True in res
		
	def get_option(self, name):
		if not name in self.__class__.__options__:
			raise KeyError, "No such option"
		return self.Settings["name"]
		
	def set_option(self, name, value):
		if not name in self.__class__.__options__:
			raise KeyError, "No such option"
		opt = self.__class__.__options__[name]
		if type(value) == opt["type"]:
			self.Settings["name"] = value
			self.option_changed(name, value)
		else:
			raise TypeError, "Wrong type, must be %s" % repr(opt["type"])
			
	def option_changed(self, name, value):
		pass
			
	def __init__(self, parent):
		super(ConfigurablePlugin, self).__init__(parent)
			
		if self.__options__ != {}:
		        self.Settings = Gio.Settings.new_with_path(BLUEMAN_PLUGINS_GSCHEMA, BLUEMAN_PLUGINS_PATH + self.__class.__name + "/")
                        #I have no idea how to implement this
                        #How can i store a list of key value pairs without knowing the key names?
                        #Or value types
			for k, v in self.__options__.iteritems():
				if self.Settings[k] == None:
					self.Settings[k] =  v["default"]

