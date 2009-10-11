# Copyright (C) 2009 Valmantas Paliksa <walmis at balticum-tv dot lt>
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

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.Sdp import *

class NMDUNSupport(AppletPlugin):
	__depends__ = ["DBusService"]
	__conflicts__ = ["PPPSupport", "NMIntegration"]
	__icon__ = "modem"
	__author__ = "Walmis"
	__description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager 0.8")
	__priority__ = 1
	
	#FIXME: watch MM signals and check if device was detected.
	
	def on_load(self, applet):
		pass
		
	def on_unload(self):
		pass
		
	def rfcomm_connect_handler(self, device, uuid, reply, err):
		uuid16 = sdp_get_serial_type(device.Address, uuid)
		if DIALUP_NET_SVCLASS_ID in uuid16:		
			device.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)
		
			return True
		else:
			return False

