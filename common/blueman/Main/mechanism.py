#
#
# mechanism.py - interface to priviledged process 
# (c) 2007 Valmantas Paliksa <walmis at balticum-tv dot lt>
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
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import os
import time
import dbus


class mechanism(dbus.proxies.Interface):
	def __init__(self):
		self.bus = dbus.SystemBus()
		
		service = self.bus.get_object("org.blueman.Mechanism", "/")
		dbus.proxies.Interface.__init__(self, service, "org.blueman.Mechanism")

