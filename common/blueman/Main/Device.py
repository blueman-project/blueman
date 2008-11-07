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


class Device:


	def __init__(self, instance):
		self.Device = instance
		
		self.Services = {}
		self.Class = 0
		
		self.GetProperties = self.Device.GetProperties
		
		self.Class = self.GetProperties()["Class"]
		
		if not "Fake" in self.Device.GetProperties():
			services = self.Device.ListServiceInterfaces()
			
			for service in services:
				name = service.GetInterfaceName().split(".")
				name = name[len(name)-1].lower()
				self.Services[name] = service
			
			
			self.HandleSignal = self.Device.HandleSignal
			self.UnHandleSignal = self.Device.UnHandleSignal
			self.GetObjectPath = self.Device.GetObjectPath

