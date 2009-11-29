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
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Config import Config
from blueman.gui.Notification import Notification
from blueman.Sdp import *
from blueman.Lib import rfcomm_list

import blueman.bluez as Bluez

import gobject
import gtk

class SerialManager(AppletPlugin):
	__icon__ = "blueman-serial"
	__author__ = "Walmis"
	__description__ = _("Standard SPP profile connection handler")
	__author__ = "walmis"
	
	def on_load(self, applet):
		pass
		
	def on_unload(self):
		pass
		
	def on_rfcomm_connected(self, device, port, uuid):
		uuid16 = sdp_get_serial_type(device.Address, uuid)
		if SERIAL_PORT_SVCLASS_ID in uuid16:
			Notification(_("Serial port connected"), _("Serial port service on device <b>%s</b> now will be available via <b>%s</b>") % (device.Alias, port), pixbuf=get_icon("blueman-serial", 48), status_icon=self.Applet.Plugins.StatusIcon)	
			
	def rfcomm_connect_handler(self, device, uuid, reply, err):
		uuid16 = sdp_get_serial_type(device.Address, uuid)
		
		if SERIAL_PORT_SVCLASS_ID in uuid16:
			device.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)
		
			return True
		else:
			return False
			
	def on_device_disconnect(self, device):
		if "serial" in device.Services:
			ports = rfcomm_list()
		
			def flt(dev):
				if dev["dst"] == device.Address and dev["state"] == "connected":
					return dev["id"]
		
			active_ports = map(flt, ports)
			
			serial = device.Services["serial"]
		
			for port in active_ports:
				if port:
					name = "/dev/rfcomm%d" % port
					try:
						serial.Disconnect(name)
					except:
						dprint("Failed to disconnect", name)
			
		
