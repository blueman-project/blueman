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
		
		self.add_dbus_method(self.DhcpClient, in_signature="s")
		
		self.Config = Config("network")
		self.Signals.Handle("gobject", self.Config, "property-changed", self.on_config_changed)
		
		self.Signals.Handle("dbus", dbus.SystemBus(), 
						self.on_network_prop_changed, 
						"PropertyChanged",
						"org.bluez.Network",
						path_keyword="path")
						
		self.dhcp_notif = None
		
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
				
	#dbus method
	def DhcpClient(self, interface):
		self.dhcp_acquire(interface)
		
	def dhcp_acquire(self, device):
		dprint("Get ip")
		if device != "":
			a= PolicyKitAuth()
			auth = a.is_authorized("org.blueman.dhcp.client")
			if not auth:
				auth = a.obtain_authorization(None, "org.blueman.dhcp.client")
			
			if auth:
				
				def reply(ip_address):

					Notification(_("Bluetooth Network"), _("Interface %(0)s bound to IP address %(1)s") % {"0": device, "1": ip_address}, 
						pixbuf=get_icon("gtk-network", 48), 
						status_icon=self.Applet.Plugins.StatusIcon)
				
				def err(msg):
					dprint(msg)
					Notification(_("Bluetooth Network"), _("Failed to obtain an IP address on %s") % (device), 
						pixbuf=get_icon("gtk-network", 48), 
						status_icon=self.Applet.Plugins.StatusIcon)
				
				Notification(_("Bluetooth Network"), _("Trying to obtain an IP address on %s\nPlease wait..." % device), 
					pixbuf=get_icon("gtk-network", 48), 
					status_icon=self.Applet.Plugins.StatusIcon)

				m = Mechanism()
				m.DhcpClient(device, reply_handler=reply, error_handler=err, timeout=120)
		
		
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
		m = Mechanism()
		m.SetGN(on)
		if self.Applet.Manager != None:
			adapters = self.Applet.Manager.ListAdapters()
			for adapter in adapters:
				s = ServiceInterface("org.bluez.NetworkHub", adapter.GetObjectPath(), ["GetProperties", "SetProperty"])
				try:
					s.SetProperty("Enabled", on)
				except:
					pass
