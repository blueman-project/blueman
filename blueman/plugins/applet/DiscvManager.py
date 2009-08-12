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
from blueman.Functions import *
from blueman.Functions import _
import gettext

from blueman.plugins.AppletPlugin import AppletPlugin

import gobject
import gtk

class DiscvManager(AppletPlugin):
	__depends__ = ["Menu"]
	__author__ = "Walmis"
	__icon__ = "gtk-find"
	__description__ = _("Provides a menu item for making the default adapter temporarily visible when it is set to hidden by default")
	
	__options__  = {
		"time" : (int,
				  60,
				  _("Discoverable timeout"),
				  _("Amount of time in seconds discoverable mode will last"),
				  60,
				  600)
	}
	
	def on_load(self, applet):
		self.item = create_menuitem(_("Make Discoverable"), get_icon("gtk-find", 16))
		applet.Plugins.Menu.Register(self, self.item, 20, False)

		self.Applet = applet
		self.adapter = None
		self.time_left = -1
			
		self.item.connect("activate", self.on_set_discoverable)
		self.item.props.tooltip_text = _("Make the default adapter temporarily visible")
		
		self.timeout = None
		
	def on_unload(self):
		self.Applet.Plugins.Menu.Unregister(self)
		del self.item
		
		if self.timeout:
			gobject.source_remove(self.timeout)
			
		if self.adapter:
			self.adapter.UnHandleSignal(self.on_adapter_property_changed, "PropertyChanged")
		
		if self.Applet.Manager:
			self.Applet.Manager.UnHandleSignal(self.on_default_adapter_changed, "DefaultAdapterChanged")
		
	def on_manager_state_changed(self, state):
		if state:
			self.init_adapter()
			self.update_menuitems()
			self.Applet.Manager.HandleSignal(self.on_default_adapter_changed, "DefaultAdapterChanged")
		else:
			if self.Applet.Manager:
				self.Applet.Manager.UnHandleSignal(self.on_default_adapter_changed, "DefaultAdapterChanged")
			
			self.adapter = None
			self.update_menuitems()
		
	def on_update(self):
		self.time_left -= 1
		self.item.get_child().props.label = _("Discoverable... %ss") % self.time_left
		self.item.props.sensitive = False

		return True
		
	def on_set_discoverable(self, item):
		if self.adapter:
			self.adapter.SetProperty("Discoverable", True)
			self.adapter.SetProperty("DiscoverableTimeout", self.get_option("time"))
		
	
	def init_adapter(self):
		try:
			self.adapter = self.Applet.Manager.GetAdapter()
		except:
			self.adapter = None
	
	def on_default_adapter_changed(self, path):
		dprint(path)
		if path != "":
			self.init_adapter()
			self.update_menuitems()
			
	def on_adapter_property_changed(self, path, key, value):
		if self.adapter and path == self.adapter.GetObjectPath():	
			dprint("prop", key, value)
			if key == "DiscoverableTimeout":
				if value == 0: #always visible
					if self.timeout != None:
						gobject.source_remove(self.timeout)
					self.time_left = -1
					self.timeout = None
				else:
					if self.time_left > -1:
						if self.timeout != None:
							gobject.source_remove(self.timeout)
					self.time_left = value

					self.timeout = gobject.timeout_add(1000, self.on_update)
					return
				
			elif (key == "Discoverable" and not value) or (key == "Powered" and not value):
				dprint("Stop")
				if self.timeout != None:
					gobject.source_remove(self.timeout)
				self.time_left = -1
				self.timeout = None

				
			self.update_menuitems()
			
			
	def update_menuitems(self):
		try:
			props = self.adapter.GetProperties()
		except Exception, e:
			dprint("warning: Adapter is None")
			self.item.props.visible = False
		else:
			if (not props["Discoverable"] or props["DiscoverableTimeout"] > 0) and props["Powered"]:
				
				self.item.props.visible = True
				self.item.get_child().props.label = _("Make Discoverable")
				self.item.props.sensitive = True

			else:
				self.item.props.visible = False

