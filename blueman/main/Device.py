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
# Device class
# acts as a caching proxy to the Bluez dbus interface
import gobject
from blueman.main.SignalTracker import SignalTracker
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device as BluezDevice
import os
import weakref
#import traceback
class Device(gobject.GObject):

	__gsignals__ = {
		'invalidated' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, ()),
		'property-changed': (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
	}
	
	def __init__(self, instance):
		gobject.GObject.__init__(self)
		
		self.Properties = {}
		self.Fake = True
		self.Temp = False
		
		if isinstance(instance, str):
			self.Device = BluezDevice(instance)
		else:
			self.Device = instance
		
		#set fallback icon, fixes lp:#327718
		self.Device.Icon = "blueman"
		self.Device.Class = "unknown"
		
		self.Services = {}

		self.Valid = True

		self.Signals = SignalTracker()
		
		dprint("caching initial properties")
		self.Properties = self.Device.GetProperties()
		
		self.init_services()
		w = weakref.ref(self)
		if not self.Fake:
			self._obj_path = self.Device.GetObjectPath()
			self.Signals.Handle("bluez", self.Device, lambda key, value: w() and w().property_changed(key, value), "PropertyChanged")
			object_path = self.Device.GetObjectPath()
			adapter = Adapter(object_path.replace("/"+os.path.basename(object_path), ""))
			self.Signals.Handle("bluez", adapter, lambda path: w() and w().on_device_removed(path), "DeviceRemoved")
	
	def __del__(self):
		dprint("deleting device", self.get_object_path())
		self.Destroy()
			
	def get_object_path(self):
		if not self.Fake:
			return self._obj_path
			
	def on_device_removed(self, path):
		if path == self._obj_path:
			self.emit("invalidated")
			self.Destroy()
	
	def init_services(self):
		dprint("Loading services")

		if not "Fake" in self.Properties:
			self.Fake = False
			services = self.Device.ListServiceInterfaces()
			self.Services = {}
			for service in services:
				name = service.GetInterfaceName().split(".")
				name = name[len(name)-1].lower()
				self.Services[name] = service
			

	def Copy(self):
		if not self.Valid:
			raise Exception, "Attempted to copy an invalidated device"
		return Device(self.Device)
	
	def property_changed(self, key, value):
		self.emit("property-changed", key, value)
		self.Properties[key] = value
		if key == "UUIDs":
			self.init_services()
			
	def Destroy(self):
		dprint("invalidating device", self.get_object_path())
		self.Valid = False
		#self.Device = None
		self.Signals.DisconnectAll()
			
	#def __del__(self):
	#	dprint("DEBUG: deleting Device instance")
			
	def GetProperties(self):
		#print "Properties requested"
		if not self.Valid:
			raise Exception, "Attempted to get properties for an invalidated device"
		return self.Properties
			
	def __getattr__(self, name):
		if name in self.__dict__["Properties"]:
			if not self.Valid:
				#traceback.print_stack()
				dprint("Warning: Attempted to get %s property for an invalidated device" % name)
			return self.__dict__["Properties"][name]
		else:
			return getattr(self.Device, name)
			
	def __setattr__(self, key, value):
		if not key in self.__dict__ and "Properties" in self.__dict__ and key in self.__dict__["Properties"]:
			if not self.Valid:
				raise Exception, "Attempted to set properties for an invalidated device"
			dprint("Setting property", key, value)
			self.__dict__["Device"].SetProperty(key, value)
		else:
			self.__dict__[key] = value
	
	
	
	
	
	

