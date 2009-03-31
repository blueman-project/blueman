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

import gobject
from blueman.main.Config import Config
import gtk

ictheme = gtk.icon_theme_get_default()

class MethodAlreadyExists(Exception):
	pass
	
class AppletPlugin(object):
	__depends__ = []
	__description__ = None
	__author__ = None
	
	__icon__ = "blueman-plugin"
	__unloadable__ = True
	__autoload__ = True
	
	__options__ = {}

	instances = []
	def __init__(self, applet):
		if not ictheme.has_icon(self.__class__.__icon__):
			self.__class__.__icon__ = "blueman-plugin"
		
		self.__opts = {}
		
		self.Applet = applet

		self.__methods = []
		self.__dbus_methods = []
		self.__dbus_signals = []
		
		AppletPlugin.instances.append(self)
		if self.__options__ != {}:
			self.__config = Config("plugins/" + self.__class__.__name__)
			 
			for k, v in self.__options__.iteritems():
				if getattr(self.__config.props, k) == None:
					setattr(self.__config.props, k, v[1])
	
	def get_option(self, name):
		if not name in self.__class__.__options__:
			raise KeyError, "No such option"
		return getattr(self.__config.props, name)
		
	def set_option(self, name, value):
		if not name in self.__class__.__options__:
			raise KeyError, "No such option"
		opt = self.__class__.__options__[name]
		if type(value) == opt[0]:
			setattr(self.__config.props, name, value)
		else:
			raise TypeError, "Wrong type, must be %s" % repr(opt[0])		
		
	def _unload(self):
		self.on_unload()
		AppletPlugin.instances.remove(self)
		for met in self.__methods:
			delattr(AppletPlugin, met)
			
		for met in self.__dbus_methods:
			self.Applet.DbusSvc.remove_registration(met)
			
		for sig in self.__dbus_signals:
			self.Applet.DbusSvc.remove_registration(sig)
		
	def __del__(self):
		print "Deleting plugin instance", self
	
	def _load(self, applet):
		self.on_load(applet)
		self.on_manager_state_changed(applet.Manager != None)
			
		
	@staticmethod
	def add_method(func):
		func.im_self.__methods.append(func.__name__)
		
		if func.__name__ in AppletPlugin.__dict__:
			raise MethodAlreadyExists
		else:
			setattr(AppletPlugin, func.__name__, func)
			
	def add_dbus_method(self, func, *args, **kwargs):
		self.Applet.DbusSvc.add_method(func, *args, **kwargs)
		self.__dbus_methods.append(func.__name__)

	def add_dbus_signal(self, func, *args, **kwargs):
		self.Applet.DbusSvc.add_signal(func, *args, **kwargs)
		self.__dbus_signals.append(func.__name__)
	
	#virtual funcs
	def on_manager_state_changed(self, state):
		pass
		
	def on_adapter_added(self, adapter):
		pass
		
	def on_adapter_removed(self, adapter):
		pass
		
	def on_adapter_property_changed(self, path, key, value):
		pass
	
	#notify when all plugins finished loading	
	def on_plugins_loaded(self):
		pass
		
	def on_load(self, applet):
		pass
	
	def on_unload(self):
		raise NotImplementedError
