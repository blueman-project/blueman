from blueman.Functions import dprint# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
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
			
		dprint("Registered modem")
		
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
			
		dprint("Unegistered modem")
		
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="s", async_callbacks=("ok","err"))
	def RfcommConnect(self, device, uuid, ok, err):
		def reply(rfcomm):
			uuid16 = uuid128_to_uuid16(uuid)
			if uuid16 == DIALUP_NET_SVCLASS_ID:
				self.RegisterModem(device, rfcomm)
				def on_propery_change(device, key, value):
					if key == "Connected":
						self.UnregisterModem(rfcomm)
						device.disconnect(id)
						device.Destroy()
						
				id = dev.connect("property-changed", on_propery_change)
			
			ok(rfcomm)

		dev = Device(BluezDevice(device))

		self.applet.recent_menu.notify(dev.Copy(), "org.bluez.Serial", [uuid] )
		
		dev.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)
		dprint("Connecting rfcomm device")
		
		
		
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="")
	def RfcommDisconnect(self, device, rfdevice):
		dev = Device(BluezDevice(device))
		dev.Services["serial"].Disconnect(rfdevice)
		self.UnregisterModem(rfdevice)
		dprint("Disonnecting rfcomm device")

		
		
	#in: interface name
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="s", out_signature="")
	def DhcpClient(self, interface):
		self.applet.NM.dhcp_acquire(interface)
		
	
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="")
	def TransferControl(self, pattern, action):
		dprint(pattern, action)
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
			dprint("Got unknown action")
		
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

	
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="b", out_signature="")
	def SetBluetoothStatus(self, status):
		self.applet.bluetooth_off = not status
	
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="", out_signature="b")
	def GetBluetoothStatus(self):
		return not self.applet.bluetooth_off
		
	@dbus.service.signal(dbus_interface='org.blueman.Applet', signature='b')
	def BluetoothStatusChanged(self, state):
		pass
		
	
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="sosas", async_callbacks=("ok","err"))
	def ServiceProxy(self, interface, object_path, _method, args, ok, err):
		bus = dbus.SystemBus()
		service = bus.get_object("org.bluez", object_path)
		method = service.get_dbus_method(_method, interface)
		
		
		if _method == "Connect":
			dev = Device(BluezDevice(object_path))
			self.applet.recent_menu.notify(dev, interface, args )
		
		
		def reply(*args):
			ok(*args)
		def error(*args):
			err(*args)
		
		method(reply_handler=reply, error_handler=error, *args)

	
	
	
