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
from blueman.Functions import _
from blueman.main.Config import Config
from blueman.bluez.ServiceInterface import ServiceInterface
from blueman.main.Mechanism import Mechanism
from blueman.main.SignalTracker import SignalTracker
from blueman.main.PolicyKitAuth import PolicyKitAuth
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
import dbus

class Networking(AppletPlugin):
	__icon__ = "network"
	__description__ = _("Provides bluetooth networking support")
	__author__ = "Walmis"
	def on_load(self, applet):
		self.Applet = applet
		self.Signals = SignalTracker()
		
		self.Config = Config("network")
		self.Signals.Handle("gobject", self.Config, "property-changed", self.on_config_changed)
		
		self.Signals.Handle("dbus", dbus.SystemBus(), 
						self.on_network_prop_changed, 
						"PropertyChanged",
						"org.bluez.Network",
						path_keyword="path")
						
		self.update_status()
		
		self.dhcp_notif = None
		
		self.load_nap_settings()
		
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
		m.NetworkSetup("reload", 0, "0", reply_handler=reply, error_handler=err)
		
	def on_unload(self):
		self.Signals.DisconnectAll()
		
	def on_adapter_added(self, path):
		self.update_status()
		
	def update_status(self):
		self.set_nap(self.Config.props.nap_enable or False)
		self.set_gn(self.Config.props.gn_enable or False)		
		
	def on_network_prop_changed(self, key, value, path):
			
		if key == "Device":
			if not self.Config.props.dhcp_client:
				if value != "":
					m = Mechanism()
					m.HalRegisterNetDev(value)
			else:
				self.dhcp_acquire(value)
		
	def dhcp_acquire(self, device):
		dprint("Get ip")
		if device != "":
			a= PolicyKitAuth()
			auth = a.is_authorized("org.blueman.dhcp.client")
			if not auth:
				auth = a.obtain_authorization(None, "org.blueman.dhcp.client")
			
			if auth:
				
				def reply(interface, condition, bound_to):
					if condition == 0:
						self.dhcp_notif.update(_("Bluetooth Network"), 
							 _("Interface %(0)s bound to IP address %(1)s") % {"0": interface, "1": bound_to})
					else:
						self.dhcp_notif.update(_("Bluetooth Network"), 
							 _("Failed to acquire an IP address on %s") % (interface))
					
					self.dhcp_notif.set_timeout(-1)
					self.dhcp_notif.show()
				
				def err(*args):
					dprint(args)
					self.dhcp_notif.update(_("Bluetooth Network"), 
						 _("Failed to acquire an IP address on %s") % (device))
					self.dhcp_notif.set_timeout(-1)
					self.dhcp_notif.show()
				
				if self.dhcp_notif != None:
					self.dhcp_notif.close()
				
				self.dhcp_notif = self.Applet.show_notification(_("Bluetooth Network"), 
								_("Acquiring an IP address on %s" % device), 0, pixbuf=get_icon("gtk-network", 48))

				m = Mechanism()
				m.DhcpClient(device, reply_handler=reply, error_handler=err)
		
		
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
				s = ServiceInterface("org.bluez.NetworkRouter", adapter.GetObjectPath(), ["GetProperties", "SetProperty"])
				try:
					s.SetProperty("Enabled", on)
				except:
					pass
				
	def set_gn(self, on):
		dprint("set gn", on)
		if self.Applet.Manager != None:
			adapters = self.Applet.Manager.ListAdapters()
			for adapter in adapters:
				s = ServiceInterface("org.bluez.NetworkHub", adapter.GetObjectPath(), ["GetProperties", "SetProperty"])
				try:
					s.SetProperty("Enabled", on)
					m = Mechanism()
					m.SetGN(on)
				except:
					pass
