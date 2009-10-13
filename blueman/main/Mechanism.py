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

import os
import time
import dbus


class Mechanism(dbus.proxies.Interface):
	__inst__ = None
	
	def __new__(c):
		if not Mechanism.__inst__:
			Mechanism.__inst__ = object.__new__(c)
		
		return Mechanism.__inst__
	
	
	def __init__(self):
		self.bus = dbus.SystemBus()
		
		service = self.bus.get_object("org.blueman.Mechanism", "/", follow_name_owner_changes=True)
		dbus.proxies.Interface.__init__(self, service, "org.blueman.Mechanism")

