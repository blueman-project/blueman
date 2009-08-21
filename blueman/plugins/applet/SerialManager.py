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
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config
from blueman.gui.Notification import Notification
from blueman.Sdp import *


import blueman.bluez as Bluez

import gobject
import gtk

class SerialManager(AppletPlugin):

	def on_load(self, applet):
		pass
		
	def on_unload(self):
		pass
		
	def on_rfcomm_connected(self, device, port, uuid):
		uuid16 = uuid128_to_uuid16(uuid)
		if uuid16 == SERIAL_PORT_SVCLASS_ID:
			Notification(_("Serial port connected"), _("Serial port service on device <b>%s</b> now will be available via <b>%s</b>") % (device.Alias, port), pixbuf=get_icon("network-wired", 48), status_icon=self.Applet.Plugins.StatusIcon)	
			
	def rfcomm_connect_handler(self, device, uuid, reply, err):
		uuid16 = uuid128_to_uuid16(uuid)
		if uuid16 == SERIAL_PORT_SVCLASS_ID:	
			device.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)
		
			return True
		else:
			return False
