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
from gi.repository import GObject
import os
from blueman.ods.OdsBase import OdsBase
from blueman.ods.OdsServer import OdsServer
from blueman.ods.OdsSession import OdsSession
from blueman.main.SignalTracker import SignalTracker
import weakref

class OdsManager(OdsBase):
	__gsignals__ = {
		'server-created' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,GObject.TYPE_STRING,)),
		'server-destroyed' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
		'session-created' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
		'session-destroyed' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
	}
	
	def __del__(self):
		dprint("deleting OdsManager instance")
			
	def __init__(self):
		OdsBase.__init__(self, "org.openobex.Manager", "/org/openobex")
		
		self.Servers = {}
		self.Sessions = {}
		
		self.Handle("SessionClosed", self.on_session_closed)
		self.Handle("SessionConnectError", self.on_session_error)
		self.Handle("SessionConnected", self.on_session_connected)
		
	def on_session_closed(self, session_path):
		dprint("__Session Closed__")
		#session_path = os.path.basename(session_path)
		if session_path in self.Sessions:
			self.Sessions[session_path].DisconnectAll()
			del self.Sessions[session_path]
			self.emit("session-destroyed", session_path)
	
	def on_session_connected(self, session_path):
		dprint("session_connected")
		#session_path = os.path.basename(session_path)
		if session_path in self.Sessions:
			session = self.Sessions[session_path]
			if not session.Connected:
				session.emit("connected")
	
	def on_session_error(self, session_path, err_name, err_msg):
		dprint("__error__")
		#session_path = os.path.basename(session_path)
		if session_path in self.Sessions:
			session = self.Sessions[session_path]
			session.emit("error-occurred", err_name, err_msg)
		
		#self.on_session_closed(session_path)

		
	def DisconnectAll(self, *args):
		def on_destroyed(inst, path):
			
			if len(self.Servers)-1 == 0:
				OdsBase.DisconnectAll(self, *args)
		
		OdsBase.GHandle(self, "server-destroyed", on_destroyed)
		if len(self.Servers) == 0:
			on_destroyed(None)
		else:	
			for k,v in self.Servers.iteritems():
				self.destroy_server(k)

	def get_server(self, pattern):
		try:
			return self.Servers[pattern]
		except KeyError:
			return None
	
	
	def create_session(self, dest_addr, source_addr="00:00:00:00:00:00", pattern="opp", error_handler=None):
		def reply(session_path):
			session = OdsSession(session_path)
			self.Sessions[session_path] = session
			self.emit("session-created", session)
		def err(*args):
			dprint("session err", args)
	
		if not error_handler:
			error_handler=err
		self.CreateBluetoothSession(dest_addr, source_addr, pattern, reply_handler=reply, error_handler=error_handler)
	
	@staticmethod
	def __server_created(ref, path, pattern):

		server = OdsServer(path)
		ref().Servers[pattern] = server
		ref().emit("server-created", server, pattern)
		
	def create_server(self, source_addr="00:00:00:00:00:00", pattern="opp", require_pairing=False):
		ref = weakref.ref(self)
	
		def err(*args):
			dprint("Couldn't create %s server" % pattern, args)
		
		self.CreateBluetoothServer(source_addr, pattern, require_pairing, reply_handler=lambda x: OdsManager.__server_created(ref, x, pattern), error_handler=err)
		
	def destroy_server(self, pattern="opp"):
		dprint("Destroy %s server" % pattern)
		def on_stopped(server):
			dprint("server stopped")
			try:
				server.Close()
			except:
				#this is a workaround for lp:735068
				dprint("DBus error on ODS server.Close()")
				#force close locally
				server.DisconnectAll()
				
			GObject.source_remove(timeout)
		
		def on_closed(server):
			dprint("server closed")
			self.emit("server-destroyed", self.Servers[pattern].object_path)
			del self.Servers[pattern]
		
		try:
			s = self.Servers[pattern]
			s.GHandle("stopped", on_stopped)
			s.GHandle("closed", on_closed)
			try:
				s.Stop()
			except:
				#ods probably died
				GObject.idle_add(on_closed, s)
				
			timeout = GObject.timeout_add(1000, on_stopped, s)
		
		except KeyError:
			pass

