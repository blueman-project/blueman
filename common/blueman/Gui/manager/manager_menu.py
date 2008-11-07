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

import gtk
import blueman.Bluez as Bluez

class manager_menu:

	def __init__(self, blueman):
		self.blueman = blueman
		
		self.Menubar = blueman.Builder.get_object("menu")
		
		self.adapter_items = []
		
		self.item_adapter = gtk.MenuItem("_Adapter")
		self.item_device = gtk.MenuItem("_Device")
		
		
		self.Menubar.append(self.item_adapter)
		self.Menubar.append(self.item_device)
		
		self.item_adapter.show()
		self.item_device.show()
		
		blueman.List.connect("adapter-added", self.on_adapter_added)
		blueman.List.connect("adapter-removed", self.on_adapter_removed)
		
		
		self.adapters = adapters = blueman.List.Manager.ListAdapters()
		
		self.generate_adapter_menu()

		
	def generate_adapter_menu(self):
		menu = gtk.Menu()
		
		sep = gtk.SeparatorMenuItem()
		sep.show()
		menu.append(sep)
		
		settings = gtk.ImageMenuItem("gtk-preferences")

		settings.show()
		menu.append(settings)
		
		group = None
		for adapter in self.adapters:
			props = adapter.GetProperties()
			item = gtk.RadioMenuItem(group, props["Name"])
			if group == None:
				group = item
			
			item.connect("activate", self.on_adapter_selected, adapter.GetObjectPath())
			if adapter.GetObjectPath() == self.blueman.List.Adapter.GetObjectPath():
				item.props.active = True
			
			item.show()
			menu.prepend(item)
		
		m = self.item_adapter.get_submenu()
		if m != None:
			m.deactivate()
		self.item_adapter.set_submenu(menu)
		
		
	def on_adapter_selected(self, menuitem, adapter_path):
		if menuitem.props.active:
			if adapter_path != self.blueman.List.Adapter.GetObjectPath():
				print "selected", adapter_path
				self.blueman.List.SetAdapter(adapter_path)
		
		
		
	def on_adapter_added(self, device_list, adapter_path):
		self.adapters.append(Bluez.Adapter(adapter_path))
		self.generate_adapter_menu()
		
	def on_adapter_removed(self, device_list, adapter_path):
		for adapter in self.adapters:
			if adapter.GetObjectPath() == adapter_path:
				self.adapters.remove(adapter)
		self.generate_adapter_menu()
		
		

	#def 
