# Copyright (C) 2009 Valmantas Paliksa <walmis at balticum-tv dot lt>
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

from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
import subprocess
import gobject
from blueman.main.NetConf import NetConf, DnsMasqHandler, DhcpdHandler

class Network(MechanismPlugin):
	def on_load(self):
		self.add_dbus_method(self.SetGN, in_signature="b", out_signature="", sender_keyword="caller")
		self.add_dbus_method(self.NetworkSetup, in_signature="sbs", out_signature="", sender_keyword="caller")
		self.add_dbus_method(self.DhcpClient, in_signature="s", out_signature="s", sender_keyword="caller", async_callbacks=("ok", "err"))
	
		self.add_dbus_method(self.EnableNetwork, in_signature="ayays", out_signature="", sender_keyword="caller", byte_arrays=True)
		self.add_dbus_method(self.DisableNetwork, in_signature="", out_signature="", sender_keyword="caller")
		self.add_dbus_method(self.ReloadNetwork, in_signature="", out_signature="", sender_keyword="caller")
	
	def DhcpClient(self, net_interface, caller, ok, err):
		self.timer.stop()

		self.confirm_authorization(caller, "org.blueman.dhcp.client")
		
		from blueman.main.DhcpClient import DhcpClient
		def dh_error(dh, message, ok, err):
			err(message)
			self.timer.resume()
		
		def dh_connected(dh, ip, ok, err):
			ok(ip)
			self.timer.resume()
		
		dh = DhcpClient(net_interface)
		dh.connect("error-occurred", dh_error, ok, err)
		dh.connect("connected", dh_connected, ok, err)		
		try:
			dh.Connect()
		except Exception, e:
			err(e)
		
	def SetGN(self, enabled, caller):
		self.timer.reset()
		if enabled:	
			p = subprocess.Popen(["/usr/sbin/avahi-autoipd", "-D", "pan0"], env=os.environ, bufsize=128)
		else:
			p = subprocess.Popen(["/usr/sbin/avahi-autoipd", "-k", "pan0"], bufsize=128)
		
		#reap the child
		gobject.child_watch_add(p.pid, lambda pid, cond: 0)
	
	def EnableNetwork(self, ip_address, netmask, dhcp_handler, caller):
		nc = NetConf.get_default()
		nc.set_ipv4(ip_address, netmask)
		eval("nc.set_dhcp_handler(%s)" % dhcp_handler)
		nc.apply_settings()
		
	def ReloadNetwork(self, caller):
		nc = NetConf.get_default()
		nc.apply_settings()
	
	def DisableNetwork(self, caller):
		nc = NetConf.get_default()
		nc.remove_settings()
		nc.set_ipv4(None, None)
		nc.store()
	
	def NetworkSetup(self, ip_address, allow_nat, server_type, caller):
		self.timer.reset()
		dprint(ip_address, allow_nat, server_type)
		if ip_address == "reload":
			info = netstatus()
			nc = None
			if info["ip"] != "0" and not nc_is_running():
				if info["type"] == "dnsmasq":
					nc = NetConfDnsMasq(None)
				elif info["type"] == "dhcpd":
					nc = NetConfDhcpd(None)
				
				if nc:
					nc.reload_settings()
			
			return
		
		self.confirm_authorization(caller, "org.blueman.network.setup")
		if ip_address == "0":
			info = netstatus()
			nc = None
			try:
				if info["type"] == "dnsmasq":
					nc = NetConfDnsMasq(None)
				elif info["type"] == "dhcpd":
					nc = NetConfDhcpd(None)
			except:
				#fallback
				nc = NetConf(None)
			
			nc.uninstall()

		else:
			if ip_chk(ip_address):
				nc = None
				if server_type == "dnsmasq":
					nc = NetConfDnsMasq(ip_address, allow_nat)
				elif server_type == "dhcpd":
					nc = NetConfDhcpd(ip_address, allow_nat)
				if nc:
					nc.install()

			else:
				return dbus.DBusException("IP Invalid")

