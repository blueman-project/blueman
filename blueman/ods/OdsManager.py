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

from blueman.ods.OdsBase import OdsBase
from blueman.ods.OdsServer import OdsServer
from blueman.main.SignalTracker import SignalTracker


class OdsManager(OdsBase):
	def __init__(self):
		OdsBase.__init__(self, "org.openobex.Manager", "/org/openobex")
		
		self.Servers = {}
	
	#@self.OdsMethod	
	def CreateBluetoothServer(self, source_addr="00:00:00:00:00:00", pattern="opp", require_paring=False):
		def reply(path):
			self.Servers[pattern] = OdsServer(path)
			
		def err(*args):
			pass
		
		OdsBase.CreateBluetoothServer(source, pattern, require_pairing, reply_handler=reply, error_handler=err)

