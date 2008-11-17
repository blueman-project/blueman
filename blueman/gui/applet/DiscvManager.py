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

from blueman.main.SignalTracker import SignalTracker
import gobject

class DiscvManager(SignalTracker):

	def __init__(self, applet):
		SignalTracker.__init__(self)
		self.Applet = applet
		self.adapter = None
		self.time_left = -1
			
		self.Handle(self.Applet.Manager, self.on_default_adapter_changed, "DefaultAdapterChanged")
		
		self.Applet.disc_items[1].connect("activate", self.on_set_discoverable)
		
		self.init_adapter()
		self.update_menuitems()
		
		self.timeout = None
		
	def on_update(self):
		self.time_left -= 1
		print self.time_left
		return True
		
	def on_set_discoverable(self, item):
		print "disc"
		
	
	def init_adapter(self):
		if self.adapter != None:
			self.adapter.UnHandleSignal(self.on_adapter_property_changed, "PropertyChanged")
		try:
			self.adapter = self.Applet.Manager.GetAdapter()
			self.adapter.HandleSignal(self.on_adapter_property_changed, "PropertyChanged")
		except:
			self.adapter = None
	
	def on_default_adapter_changed(self, path):
		print path
		if path != "":
			self.init_adapter()
			
	def on_adapter_property_changed(self, key, value):
		print "prop", key, value
		if key == "DiscoverableTimeout":
			if value == 0: #always visible
				if self.timeout != None:
					gobject.source_remove(self.timeout)
				self.time_left = -1
				self.timeout = None
			else:
				self.time_left = value
				self.timeout = gobject.timeout_add(1000, self.on_update)
				
		self.update_menuitems()
			
			
	def update_menuitems(self):
		try:
			props = self.adapter.GetProperties()
		except:
			for item in self.Applet.disc_items:
				item.props.visible = False
		else:
			if not props["Discoverable"] or props["DiscoverableTimeout"] > 0:
				for item in self.Applet.disc_items:
					item.props.visible = True
			else:
				for item in self.Applet.disc_items:
					item.props.visible = False
		
		
