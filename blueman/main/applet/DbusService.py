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
import dbus
import dbus.glib
import dbus.service

import gtk

from blueman.main.PolicyKitAuth import PolicyKitAuth
from blueman.main.Mechanism import Mechanism
from blueman.bluez.Device import Device as BluezDevice
from blueman.main.Device import Device
from blueman.Sdp import *

class DbusService(dbus.service.Object):
	def __init__(self, applet):
		self.applet = applet
		self.bus = dbus.SessionBus();
		self.bus.request_name("org.blueman.Applet")
		dbus.service.Object.__init__(self, self.bus, "/")
		
		
	
	#in: bluez_device_path, rfcomm_device
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="")
	def RegisterModem(self, device_path, rfcomm_device):
		a = PolicyKitAuth()
		authorized = a.is_authorized("org.blueman.hal.manager")
		if not authorized:
			authorized = a.obtain_authorization(False, "org.blueman.hal.manager")
		
		if authorized:
			dev = BluezDevice(device_path)
			props = dev.GetProperties()
			
			m = Mechanism()
			m.HalRegisterModemPort(rfcomm_device, props["Address"])
			
		print "Registered modem"
		
	#in: bluez_device_path, rfcomm_device
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="s", out_signature="")
	def UnregisterModem(self, device):
		a = PolicyKitAuth()
		authorized = a.is_authorized("org.blueman.hal.manager")
		if not authorized:
			authorized = a.obtain_authorization(False, "org.blueman.hal.manager")
		
		if authorized:
			m = Mechanism()
			m.HalUnregisterModemPortDev(device)
			
		print "Unegistered modem"
		
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="s", async_callbacks=("ok","err"))
	def RfcommConnect(self, device, uuid, ok, err):
		def reply(rfcomm):
			uuid16 = uuid128_to_uuid16(uuid)
			if uuid16 == DIALUP_NET_SVCLASS_ID:
				self.RegisterModem(device, rfcomm)
			
			ok(rfcomm)

		dev = Device(BluezDevice(device))
		dev.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)
		print "Connecting rfcomm device"
		
		
		
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="")
	def RfcommDisconnect(self, device, rfdevice):
		dev = Device(BluezDevice(device))
		dev.Services["serial"].Disconnect(rfdevice)
		self.UnregisterModem(rfdevice)
		print "Disonnecting rfcomm device"

		
		
	#in: interface name
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="s", out_signature="")
	def DhcpClient(self, interface):
		print "run dhcp"
		
	
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="")
	def TransferControl(self, pattern, action):
		print pattern, action
		if action == "destroy":
			self.applet.Transfer.destroy_server(pattern)
		elif action == "stop":
			server = self.applet.Transfer.get_server(pattern)
			if server != None:
				server.Stop()
		
		elif action == "create":
			self.applet.Transfer.create_server(pattern)
			
		elif action == "start":
			self.applet.Transfer.start_server(pattern)
		
		
		else:
			print "Got unknown action"
		
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="s", out_signature="u")
	def TransferStatus(self, pattern):
		server = self.applet.Transfer.get_server(pattern)
		if server != None:
			if server.IsStarted():
				return 2
			else:
				return 1
		else:
			return 0
	
	
