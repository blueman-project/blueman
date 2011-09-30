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
from blueman.main.Config import Config
from blueman.bluez.ServiceInterface import ServiceInterface
from blueman.main.Mechanism import Mechanism
from blueman.main.SignalTracker import SignalTracker

from blueman.plugins.AppletPlugin import AppletPlugin

import dbus

class Networking(AppletPlugin):
	__icon__ = "network"
	__description__ = _("Manages local network services, like NAP bridges")
	__author__ = "Walmis"
	
	def on_load(self, applet):
		self.Applet = applet
		self.Signals = SignalTracker()
		
		self.Config = Config("network")
		self.Signals.Handle("gobject", self.Config, "property-changed", self.on_config_changed)
		
		self.load_nap_settings()
		
	def on_manager_state_changed(self, state):
		if state:
			self.update_status()
		
	def load_nap_settings(self):
		dprint("Loading NAP settings")
		def reply():
			pass
		def err(excp):
			lines = str(excp).splitlines()
			d = gtk.MessageDialog( None, buttons=gtk.BUTTONS_OK, type=gtk.MESSAGE_ERROR)
			d.props.text = _("Failed to apply network settings")
			d.props.secondary_text = lines[-1] + "\n\n"+_("You might not be able to connect to the Bluetooth network via this machine")
			d.run()
			d.destroy()
		
		m = Mechanism()
		m.ReloadNetwork(reply_handler=reply, error_handler=err)
		
	def on_unload(self):
		self.Signals.DisconnectAll()
		
	def on_adapter_added(self, path):
		self.update_status()
		
	def update_status(self):
		self.set_nap(self.Config.props.nap_enable or False)
		self.set_gn(self.Config.props.gn_enable or False)		


	def on_config_changed(self, config, key, value):
		if key == "nap_enable":
			self.set_nap(value)
		elif key == "gn_enable":
			self.set_gn(value)
		
		
	def set_nap(self, on):
		dprint("set nap", on)
		if self.Applet.Manager != None:
			adapters = self.Applet.Manager.ListAdapters()
			for adapter in adapters:
				s = ServiceInterface("org.bluez.NetworkServer", adapter.GetObjectPath(), ["Register", "Unregister"])
				if on:
					s.Register("nap", "pan1")
				else:
					s.Unregister("nap")

				
	def set_gn(self, on):
		#latest bluez does not support gn
		pass
#		dprint("set gn", on)
#		m = Mechanism()
#		m.SetGN(on, reply_handler=(lambda *args: None), error_handler=(lambda *args: None))
#
#		if self.Applet.Manager != None:
#			adapters = self.Applet.Manager.ListAdapters()
#			for adapter in adapters:
#				s = ServiceInterface("org.bluez.NetworkServer", adapter.GetObjectPath(), ["Register", "Unregister"])
#				if on:
#					s.Register("gn", "pan0")
#				else:
#					s.Unregister("gn")
