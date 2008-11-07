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

class ManagerDeviceMenu:

	def __init__(self, blueman):
		
		self.Menu = gtk.Menu()

		self.Device = blueman.List.get(blueman.List.selected(), "device")["device"]
		
		self.generate_menu()
		
	def generate_menu(self):
		props = self.Device.GetProperties()
		if "Fake" in props:
			print "fake device"
			
			
		else:
			for name, service in self.Device.Services.iteritems():
				if name == "serial":
					uuids = props["UUIDs"]
					for uuid in uuids:
						uuid = uuid128_to_uuid16(uuid)
						if uuid == SERIAL_PORT_SVCLASS_ID:
							print "spp"
							
						if uuid == DIALUP_NET_SVCLASS_ID:
							print "dun"
				
				
			print "real device"
		
