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
from blueman.main.Mechanism import Mechanism
from blueman.main.PolicyKitAuth import PolicyKitAuth
from blueman.Functions import get_icon
import gettext

_ = gettext.gettext

class NetworkManager():

	def __init__(self, applet):
		self.Applet = applet
		
		self.Config = Config("network")
		self.Applet.Signals.Handle("gobject", self.Config, "property-changed", self.on_config_changed)
		
		self.Applet.Signals.Handle("dbus", self.Applet, 
						self.on_network_prop_changed, 
						"PropertyChanged",
						"org.bluez.Network",
						path_keyword="path")
						
		
		self.set_nap(self.Config.props.nap_enable or False)
		self.set_gn(self.Config.props.gn_enable or False)
		
		self.dhcp_notif = None
	
	def __del__(self):
		print "networkmanager deleted"
		
	def on_network_prop_changed(self, key, value, path):
		if self.Config.props.dhcp_client == None:
			self.Config.props.dhcp_client = True
			
		if not self.Config.props.dhcp_client:
			return
		if key == "Device":
			self.dhcp_acquire(value)
		
	def dhcp_acquire(self, device):
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
					
					self.dhcp_notif = None
				
				def err(*args):
					print args
					self.dhcp_notif.update(_("Bluetooth Network"), 
						 _("Failed to acquire an IP address on %s") % (device))
					self.dhcp_notif.set_timeout(-1)
					self.dhcp_notif.show()
					self.dhcp_notif = None
				
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
