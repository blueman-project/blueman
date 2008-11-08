#
#
# hal_manager.py
# (c) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
import dbus
import re



class HalManager(dbus.proxies.Interface):
	ports = []
	layer = None
	def __init__(self):
		self.bus = dbus.SystemBus()
		obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
		dbus.proxies.Interface.__init__(self, obj, 'org.freedesktop.Hal.Manager')
		

	def register(self, device_file, bd_addr):
	
		ref = self.NewDevice()
		#print ref
		
		existing = self.FindDeviceStringMatch("serial.device", device_file)

		if len(existing) > 0:
			return False		
		
		
		r = re.search("rfcomm([0-9]*)$", device_file)
		portid = int(r.groups()[0])
		

		obj = self.bus.get_object('org.freedesktop.Hal', ref)
		device = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

		dev = self.FindDeviceStringMatch("info.product", "Bluetooth RFCOMM")
		if len(dev) == 0:
			dev = self._create_layer()
		else:
			dev = dev[0]

		device.SetPropertyString("info.category", "serial")
		device.SetPropertyString("info.parent", dev)
		device.SetPropertyString("info.bluetooth_address", bd_addr)
		device.SetPropertyString("info.product", "DUN (%s)" % (bd_addr))
		device.SetPropertyString("info.vendor", "Bluetooth")

		device.SetPropertyInteger("serial.port", portid)
		device.SetPropertyString("serial.device", device_file)
		device.SetPropertyString("linux.device_file", device_file)
		device.SetPropertyString("serial.type", "unknown")

		device.SetPropertyString("serial.originating_device", "/org/freedesktop/Hal/devices/%s" % "rfcomm%s" % portid)	

		device.StringListAppend("modem.command_sets", "GSM-07.07")
		device.StringListAppend("modem.command_sets", "GSM-07.05")

		device.AddCapability("serial")
		device.AddCapability("modem")


		self.CommitToGdl(ref, "/org/freedesktop/Hal/devices/%s" % "rfcomm%s" % portid)
		
		return True
		
	def _create_layer(self):
		ref = self.NewDevice()

		obj = self.bus.get_object('org.freedesktop.Hal', ref)
		device = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

		bt_adapter = self.FindDeviceByCapability("bluetooth_hci");

		device.SetPropertyString("info.linux.driver", "rfcomm")
		device.SetPropertyString("info.parent", bt_adapter[0])
		device.SetPropertyString("info.product", "Bluetooth RFCOMM")

		self.CommitToGdl(ref, "/org/freedesktop/Hal/devices/bt_rfcomm_layer")
		
		return "/org/freedesktop/Hal/devices/bt_rfcomm_layer"
		
	def remove_all(self):
		devs = self.FindDeviceStringMatch("info.product", "Bluetooth RFCOMM")
		for dev in devs:
			ports = self.FindDeviceStringMatch("info.parent", dev)
			for port in ports:
				self.Remove(port)
			
			self.Remove(dev)
			
			
	def unregister_dev(self, device_file):
		ports = self.FindDeviceStringMatch("serial.device", device_file)
		for port in ports:
			self.Remove(port)
			
	def unregister_addr(self, dev_address):
		ports = self.FindDeviceStringMatch("info.bluetooth_address", device_file)
		for port in ports:
			self.Remove(port)
	
	def exists(self, device_file):
		ports = self.FindDeviceStringMatch("serial.device", device_file)
		return len(ports) > 0
			
			
	
			
		
		
		
