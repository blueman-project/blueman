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
from blueman.Functions import dprint


class DhcpClient(gobject.GObject):
	__gsignals__ = {
		#arg: interface name eg. ppp0
		'connected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'error-occurred' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
	}	
	
	def __init__(self, interface):
		gobject.GObject.__init__(self)
	
		self.interface = interface
	
		try:
			self.dhclient = subprocess.Popen(["dhclient", "-e", "IF_METRIC=100", "-1", interface])
		except:
			raise Exception("dhclient binary not found")
			
		gobject.timeout_add(1000, self.check_dhclient)

	def get_ip_address(self, ifname):
		SIOCGIFADDR = 0x8915
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		return socket.inet_ntoa(fcntl.ioctl(s.fileno(), SIOCGIFADDR, struct.pack('256s', ifname[:15]))[20:24])		
		
	def check_dhclient(self):
		status = self.dhclient.poll()
		if status != None:
			if status == 0:
				ip = self.get_ip_address(self.interface)
				dprint("bound to", ip)
				self.emit("connected", ip)
				return False
			else:
				dprint("dhclient failed with status code", status)
				self.emit("error-occurred", status)
				return False
			
		return True		
