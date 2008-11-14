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
import gobject

from blueman.ods.OdsBase import OdsBase
from blueman.ods.OdsServer import OdsServer
from blueman.main.SignalTracker import SignalTracker


class OdsManager(OdsBase):
	__gsignals__ = {
		'server-created' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'server-destroyed' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),

	}
	
	def __init__(self):
		OdsBase.__init__(self, "org.openobex.Manager", "/org/openobex")
		
		self.bus.watch_name_owner('org.openobex', self.on_dbus_name_owner_change)
		
		self.Servers = {}

	def on_dbus_name_owner_change(self, owner):
		print "name ch", owner
		#if owner == '':
			
		#else:
			
		
	def DisconnectAll(self, *args):
		for k,v in self.Server.iteritems():
			v.DisconnectAll()
		self.Servers = {}
		OdsBase.DisconnectAll(self, *args)
		
	
	#@self.OdsMethod	
	def create_server(self, source_addr="00:00:00:00:00:00", pattern="opp", require_pairing=False):
		def reply(path):
			server = OdsServer(path)
			self.emit("server-created", server)
			self.Servers[pattern] = server
			
		def err(*args):
			pass
		
		self.CreateBluetoothServer(source_addr, pattern, require_pairing, reply_handler=reply, error_handler=err)

