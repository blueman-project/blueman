#
#
# blueman
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
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#


class Device:


	def __init__(self, instance):
		self.Device = instance
		
		self.Services = None
		self.Class = 0
		
		self.GetProperties = self.Device.GetProperties
		
		self.Class = self.GetProperties()["Class"]
		
		if not "Fake" in self.Device.GetProperties():
			self.Services = self.Device.ListServiceInterfaces()
			
			
			self.HandleSignal = self.Device.HandleSignal
			self.UnHandleSignal = self.Device.UnHandleSignal
			self.GetObjectPath = self.Device.GetObjectPath

