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
from blueman.main.SignalTracker import SignalTracker

class Device:


	def __init__(self, instance):
		self.Properties = {}
		self.Fake = True
		
		self.Device = instance
		
		self.Services = {}


		self.Signals = SignalTracker()
		
		
		print "caching initial properties"
		self.Properties = self.Device.GetProperties()
		
		self.init_services()
			
	
	def init_services(self):
		print "Loading services"
		self.Signals.DisconnectAll()
		if not "Fake" in self.Properties:
			self.Fake = False
			services = self.Device.ListServiceInterfaces()
			self.Signals.Handle(self.Device, self.property_changed, "PropertyChanged")
			for service in services:
				name = service.GetInterfaceName().split(".")
				name = name[len(name)-1].lower()
				self.Services[name] = service

				
			
	
	def property_changed(self, key, value):
		self.Properties[key] = value
		if key == "UUIDs":
			self.init_services()
			
	def Destroy(self):
		self.Signals.DisconnectAll()
			
	#def __del__(self):
	#	print "DEBUG: deleting Device instance"
			
	def GetProperties(self):
		#print "Properties requested"
		return self.Properties
			
	def __getattr__(self, name):
		
		if name in self.__dict__["Properties"]:
			return self.__dict__["Properties"][name]
		else:
			return getattr(self.Device, name)
			
	def __setattr__(self, key, value):
		if not key in self.__dict__ and "Properties" in self.__dict__ and key in self.__dict__["Properties"]:
			print "Setting property", key, value
			self.__dict__["Device"].SetProperty(key, value)
		else:
			self.__dict__[key] = value
	
	
	
	
	
	

