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
import socket
import fcntl
from gi.repository import GObject
import struct
import subprocess
from blueman.Lib import get_net_address


class DhcpClient(GObject.GObject):
	__gsignals__ = {
		#arg: interface name eg. ppp0
		'connected' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
		'error-occurred' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
	}	
	
	quering = []
	
	def __init__(self, interface, timeout=30):
		GObject.GObject.__init__(self)
	
		self.interface = interface
		self.timeout = timeout
		
		self.DHCP_CLIENT = False
		try:
			self.dhclient = subprocess.Popen(["dhclient", "--version"])
			self.dhclient.terminate()
			self.DHCP_CLIENT = "DHCLIENT"
		except OSError:
			try:
				self.dhcpcd = subprocess.Popen(["dhcpcd", "--version"])
				self.dhcpcd.terminate()
				self.DHCP_CLIENT = "DHCPCD"
			except OSError:
				self.DHCP_CLIENT = "NONE"
	
	def Connect(self):
		if self.DHCP_CLIENT == "NONE":
			raise Exception("no DHCP client found, please install dhcpcd or dhclient")

		if self.interface in DhcpClient.quering:
			raise Exception("DHCP already running on this interface")
		else:
			DhcpClient.quering.append(self.interface)

		if self.DHCP_CLIENT == "DHCLIENT":
			try:	
				self.dhclient = subprocess.Popen(["dhclient", "-e", "IF_METRIC=100", "-1", self.interface])
			except:
				#Should never happen now...
				raise Exception("dhclient binary not found")
			GObject.timeout_add(1000, self.check_dhclient)
		elif self.DHCP_CLIENT == "DHCPCD":
			try:	
				self.dhcpcd = subprocess.Popen(["dhcpcd", "-m", "100", self.interface])
			except: 
				#Should never happen now...
				raise Exception("dhcpcd binary not found")		
			GObject.timeout_add(1000, self.check_dhcpcd)

		GObject.timeout_add(self.timeout*1000, self.on_timeout)

		
	def on_timeout(self):
		if self.DHCP_CLIENT == "DHCLIENT":
			if self.dhclient.poll() == None:
				dprint("Timeout reached, terminating dhclient")
				self.dhclient.terminate()
		elif self.DHCP_CLIENT == "DHCPCD":
			if self.dhcpcd.poll() == None:
				dprint("Timeout reached, terminating dhcpcd")
				self.dhcpcd.terminate()
		
	def check_dhclient(self):
		status = self.dhclient.poll()
		if status != None:
			if status == 0:
				def complete():
					ip = get_net_address(self.interface)
					dprint("bound to", ip)
					self.emit("connected", ip)	
				
				GObject.timeout_add(1000, complete)
				DhcpClient.quering.remove(self.interface)
				return False
				
			else:
				dprint("dhcp client failed with status code", status)
				self.emit("error-occurred", status)
				DhcpClient.quering.remove(self.interface)
				return False
			
		return True	
	
	def check_dhcpcd(self):
		status = self.dhcpcd.poll()
		if status != None:
			if status == 0:
				def complete():
					ip = get_net_address(self.interface)
					dprint("bound to", ip)
					self.emit("connected", ip)	
				
				GObject.timeout_add(1000, complete)
				DhcpClient.quering.remove(self.interface)
				return False
				
			else:
				dprint("dhcpcd failed with status code", status)
				self.emit("error-occurred", status)
				DhcpClient.quering.remove(self.interface)
				return False
			
		return True		
