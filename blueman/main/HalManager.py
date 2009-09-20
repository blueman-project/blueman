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
import re
from blueman.Lib import probe_modem
import os
import gobject

def mkname():
    i = 0
    while 1:
        i += 1
        yield "/lib/udev/rules.d/33-%d-blueman.rules" % i
name = mkname()

def getUniqueSynset(hasDupes):
	unique_trick = [ uniq for uniq in hasDupes if uniq not in locals()['_[1]'] ]
	return unique_trick
									        
class HalManager(dbus.proxies.Interface):
	ports = []
	layer = None
	def __init__(self):
		self.bus = dbus.SystemBus()
		obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
		dbus.proxies.Interface.__init__(self, obj, 'org.freedesktop.Hal.Manager')
		
	
	def register_netdev(self, devicename):
		def reg():
			devices = self.FindDeviceStringMatch("net.interface", devicename)
			if len(devices):
				for device in devices:
					obj = self.bus.get_object('org.freedesktop.Hal', device)
					device = dbus.Interface(obj, 'org.freedesktop.Hal.Device')
					device.SetPropertyString("info.category", "net.80203")
					device.AddCapability("net.80203")
		gobject.timeout_add(1000, reg)

	def register(self, device_file, bd_addr, ok, err):

		existing = self.FindDeviceStringMatch("serial.device", device_file)

		if len(existing) > 0:
			dprint("Already registered")
			ok()
			return	
		
		ref = self.NewDevice()
		r = re.search("rfcomm([0-9]*)$", device_file)
		portid = int(r.groups()[0])
		

		obj = self.bus.get_object('org.freedesktop.Hal', ref)
		device = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

		dev = self.FindDeviceStringMatch("info.product", "Bluetooth RFCOMM")
		if len(dev) == 0:
			dev = self._create_layer()
		else:
			dev = dev[0]
		
		def probe_response(capabilities):
			dprint("Device capabilities: %s" % capabilities)

			if capabilities == None or capabilities == []:
				dprint("Removing temp UDI")
				err(Exception)
			else:
				ok()
				try:
					dprint("Generating udev rule")
					rule_file = name.next()
					rule = open(rule_file, "w")
					rule.write("DEVPATH==\"*/rfcomm%d\", ENV{ID_NM_MODEM_PROBED}=\"1\", " % portid)
					caps = []
					for cap in capabilities:
						if cap == "GSM-07.07" or cap == "GSM-07.05":
							caps.append("ENV{ID_NM_MODEM_GSM}=\"1\"")
						elif cap == "IS-707-A" or cap == "IS-707-P":
							caps.append("ENV{ID_NM_MODEM_IS707_A}=\"1\"")
						elif cap == "IS-856":
							caps.append("ENV{ID_NM_MODEM_IS856}=\"1\"")
						elif cap == "IS-856-A":
							caps.append("ENV{ID_NM_MODEM_IS856_A}=\"1\"")
							
					caps = getUniqueSynset(caps)
					rule.write(", ".join(caps))
					rule.close()
					
				except IOError:
					dprint("Failed to generate udev rule")
				
				else:
					#this causes hal to register a rfcomm device
					uevent = open("/sys/class/tty/rfcomm%s/uevent" % portid, "w")
					uevent.write("change")
					uevent.close()
					
					
				def check_hal(device):
					found_devs = self.FindDeviceStringMatch("linux.device_file", "/dev/rfcomm%d" % portid)
					if len(found_devs):
						self.Remove(found_devs[0])

					dprint("Adding our own rfcomm device to hal")
					device.SetPropertyString("info.category", "serial")
					device.SetPropertyString("info.parent", dev)
					device.SetPropertyString("info.bluetooth_address", bd_addr)
					device.SetPropertyString("info.product", "DUN (%s)" % (bd_addr))
					device.SetPropertyString("info.vendor", "Bluetooth")
					device.SetPropertyString("info.linux.driver", "rfcomm")
					device.SetPropertyString("linux.sysfs_path", "/sys/class/tty/rfcomm%s" % portid) 

					device.SetPropertyInteger("serial.port", portid)
					device.SetPropertyString("serial.device", device_file)
					device.SetPropertyString("linux.device_file", device_file)
					device.SetPropertyString("serial.type", "unknown")

					device.SetPropertyString("serial.originating_device", "/org/freedesktop/Hal/devices/%s" % "rfcomm%s" % portid)

					device.AddCapability("serial")
					device.AddCapability("modem")	
					device.SetMultipleProperties({"modem.command_sets": capabilities})
				
					self.CommitToGdl(ref, "/org/freedesktop/Hal/devices/%s" % "rfcomm%s" % portid)
						
					gobject.timeout_add(1000, os.unlink, rule_file)
		
				gobject.timeout_add(1000, check_hal, device)
		
		dprint("Probing device %s for capabilities" % device_file)
		probe_modem(device_file, probe_response)
		
	def _create_layer(self):
		ref = self.NewDevice()

		obj = self.bus.get_object('org.freedesktop.Hal', ref)
		device = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

		bt_adapter = self.FindDeviceByCapability("bluetooth_hci");

		device.SetPropertyString("info.linux.driver", "rfcomm")
		try:
			device.SetPropertyString("info.parent", bt_adapter[0])
		except:
			pass
			
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
		
