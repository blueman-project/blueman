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

from gi.repository import GObject

from gi.repository import Gtk
import traceback

from blueman.plugins.ConfigurablePlugin import ConfigurablePlugin
from functools import partial

ictheme = Gtk.IconTheme.get_default()

class MethodAlreadyExists(Exception):
	pass
	
class AppletPlugin(ConfigurablePlugin):
	__icon__ = "blueman-plugin"
	
	def __init__(self, applet):
		super(AppletPlugin, self).__init__(applet)
		
		if not ictheme.has_icon(self.__class__.__icon__):
			self.__class__.__icon__ = "blueman-plugin"
		
		self.__opts = {}
		
		self.Applet = applet

		#self.__methods = []
		self.__dbus_methods = []
		self.__dbus_signals = []
		
		self.__overrides = []
		
	def override_method(self, object, method, override):
		orig = object.__getattribute__(method)
		object.__setattr__(method, partial(override, object))
		self.__overrides.append((object, method, orig))
		
	def _unload(self):
		for (object, method, orig) in self.__overrides:
			object.__setattr__(method, orig)
		
		super(AppletPlugin, self)._unload()
		
		for met in self.__dbus_methods:
			self.Applet.DbusSvc.remove_registration(met)
			
		for sig in self.__dbus_signals:
			self.Applet.DbusSvc.remove_registration(sig)
		

	def _load(self, applet):
		super(AppletPlugin, self)._load(applet)
		
		self.on_manager_state_changed(applet.Manager != None)

			
	def add_dbus_method(self, func, *args, **kwargs):
		self.Applet.DbusSvc.add_method(func, *args, **kwargs)
		self.__dbus_methods.append(func.__name__)

	def add_dbus_signal(self, func, *args, **kwargs):
		self.__dbus_signals.append(func)
		return self.Applet.DbusSvc.add_signal(func, *args, **kwargs)
		
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
