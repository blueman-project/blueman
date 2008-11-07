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
from blueman.Sdp import *
from blueman.Functions import *

import gettext
_ = gettext.gettext

class ManagerDeviceMenu:

	def __init__(self, blueman, menushell=None):
		if menushell == None:
			self.Menu = gtk.Menu()
		else:
			self.Menu = menushell

		self.Device = blueman.List.get(blueman.List.selected(), "device")["device"]
		
		self.generate_menu()
		
		
	def create_menuitem(self, text, image):
		item = gtk.ImageMenuItem()
		item.set_image(gtk.image_new_from_pixbuf(image))
		
		label = gtk.Label()
		label.set_text(text)
		label.set_alignment(0,0.5)

		label.show()
		
		item.add(label)
		
		return item
		
	def generate_menu(self):
		props = self.Device.GetProperties()
		if "Fake" in props:
			print "fake device"
			
			
		else:
			for name, service in self.Device.Services.iteritems():
				if name == "serial":
					uuids = props["UUIDs"]
					
					item = self.create_menuitem(_("Serial Ports"), get_icon("modem", 16))
					sub = gtk.Menu()
					sub.show()
					item.set_submenu(sub)
					item.show()
					self.Menu.append(item)
					for uuid in uuids:
						
						uuid16 = uuid128_to_uuid16(uuid)
						if uuid16 == SERIAL_PORT_SVCLASS_ID:
							item = self.create_menuitem(_("Dialup Service"), get_icon("modem", 16))
							sub.append(item)
							item.show()
							
						if uuid16 == DIALUP_NET_SVCLASS_ID:
							item = self.create_menuitem(_("Serial Service"), get_icon("modem", 16))
							sub.append(item)
							item.show()
							
					
				if name == "input":
					sprops = service.GetProperties()
					print props
					print sprops
					if sprops["Connected"]:
						item = self.create_menuitem(_("Disconnect Input Service"), get_icon("mouse", 16))
					else:
						item = self.create_menuitem(_("Connect Input Service"), get_icon("mouse", 16))
					item.show()
					self.Menu.append(item)
					
				if name == "network":
					sprops = service.GetProperties()
					
					print sprops
					if sprops["Connected"]:
						item = self.create_menuitem(_("Disconnect Network Service"), get_icon("network", 16))
					else:
						item = self.create_menuitem(_("Connect Network Service"), get_icon("network", 16))
					item.show()
					self.Menu.append(item)
				
			print "real device"
		
