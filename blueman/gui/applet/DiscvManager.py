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
import gettext
from blueman.Functions import dprint
_ = gettext.gettext

class DiscvManager:

	def __init__(self, applet):

		self.Applet = applet
		self.adapter = None
		self.time_left = -1
			
		self.Applet.Signals.Handle(self.Applet.Manager, self.on_default_adapter_changed, "DefaultAdapterChanged")
		
		self.Applet.Signals.Handle(self.Applet.disc_item, "activate", self.on_set_discoverable)
		self.Applet.disc_item.props.tooltip_text = _("Make the default adapter visible for 1 minute")
		
		self.init_adapter()
		self.update_menuitems()
		
		self.timeout = None
		
	def on_update(self):
		self.time_left -= 1
		self.Applet.disc_item.get_child().props.label = _("Discoverable... %ss") % self.time_left
		self.Applet.disc_item.props.sensitive = False

		return True
		
	def on_set_discoverable(self, item):
		if self.adapter:
			self.adapter.SetProperty("Discoverable", True)
			self.adapter.SetProperty("DiscoverableTimeout", 60)
		
	
	def init_adapter(self):
		if self.adapter != None:
			self.adapter.UnHandleSignal(self.on_adapter_property_changed, "PropertyChanged")
		try:
			self.adapter = self.Applet.Manager.GetAdapter()
			self.Applet.Signals.Handle(self.adapter, self.on_adapter_property_changed, "PropertyChanged")
		except:
			self.adapter = None
	
	def on_default_adapter_changed(self, path):
		dprint(path)
		if path != "":
			self.init_adapter()
			
	def on_adapter_property_changed(self, key, value):
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
			self.Applet.disc_item.props.visible = False
		else:
			if (not props["Discoverable"] or props["DiscoverableTimeout"] > 0) and props["Powered"]:
				
				self.Applet.disc_item.props.visible = True
				self.Applet.disc_item.get_child().props.label = _('Make Discoverable')
				self.Applet.disc_item.props.sensitive = True

			else:
				self.Applet.disc_item.props.visible = False
		
		
