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
import gobject
import struct
import subprocess
from blueman.Lib import get_net_address


class DhcpClient(gobject.GObject):
	__gsignals__ = {
		#arg: interface name eg. ppp0
		'connected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'error-occurred' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
	}	
	
	quering = []
	
	def __init__(self, interface, timeout=30):
		gobject.GObject.__init__(self)
	
		self.interface = interface
		self.timeout = timeout
	
	def Connect(self):
		if self.interface in DhcpClient.quering:
			raise Exception("dhclient already running on this interface")
		else:
			DhcpClient.quering.append(self.interface)
			
		try:
			self.dhclient = subprocess.Popen(["dhclient", "-e", "IF_METRIC=100", "-1", self.interface])
		except:
			raise Exception("dhclient binary not found")
			
		gobject.timeout_add(1000, self.check_dhclient)
		gobject.timeout_add(self.timeout*1000, self.on_timeout)

		
	def on_timeout(self):
		if self.dhclient.poll() == None:
			dprint("Timeout reached, terminating dhclient")
			self.dhclient.terminate()
		
	def check_dhclient(self):
		status = self.dhclient.poll()
		if status != None:
			if status == 0:
				def complete():
					ip = get_net_address(self.interface)
					dprint("bound to", ip)
					self.emit("connected", ip)	
				
				gobject.timeout_add(1000, complete)
				DhcpClient.quering.remove(self.interface)
				return False
				
			else:
				dprint("dhclient failed with status code", status)
				self.emit("error-occurred", status)
				DhcpClient.quering.remove(self.interface)
				return False
			
		return True		
