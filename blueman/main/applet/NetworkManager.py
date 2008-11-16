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
from blueman.main.Config import Config
from blueman.bluez.ServiceInterface import ServiceInterface

class NetworkManager():

	def __init__(self, applet):
		self.Applet = applet
		
		self.Config = Config("network")
		self.Applet.Signals.Handle("gobject", self.Config, "property-changed", self.on_config_changed)
		
		self.set_nap(self.Config.props.nap_enable or False)
		self.set_gn(self.Config.props.gn_enable or False)
		
	def __del__(self):
		print "networkmanager deleted"
		
		
	def on_config_changed(self, config, key, value):
		if key == "nap_enable":
			self.set_nap(value)
		elif key == "gn_enable":
			self.set_gn(value)
		
		
	def set_nap(self, on):
		print "set nap", on
		if self.Applet.Manager != None:
			adapters = self.Applet.Manager.ListAdapters()
			for adapter in adapters:
				s = ServiceInterface("org.bluez.NetworkRouter", adapter.GetObjectPath(), ["GetProperties", "SetProperty"])
				try:
					s.SetProperty("Enabled", on)
				except:
					pass
				
	def set_gn(self, on):
		print "set gn", on
		if self.Applet.Manager != None:
			adapters = self.Applet.Manager.ListAdapters()
			for adapter in adapters:
				s = ServiceInterface("org.bluez.NetworkHub", adapter.GetObjectPath(), ["GetProperties", "SetProperty"])
				try:
					s.SetProperty("Enabled", on)
				except:
					pass
