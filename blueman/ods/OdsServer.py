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
from blueman.ods.OdsBase import OdsBase
from blueman.ods.OdsServerSession import OdsServerSession

class OdsServer(OdsBase):
	__gsignals__ = {
		'started' : (GObject.SignalFlags.NO_HOOKS, None, ()),
		'stopped' : (GObject.SignalFlags.NO_HOOKS, None, ()),
		'closed' : (GObject.SignalFlags.NO_HOOKS, None, ()),
		'error-occured' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
		'session-created' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
		'session-removed' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
	}
	
	def __init__(self, obj_path):
		OdsBase.__init__(self, "org.openobex.Server", obj_path)
		
		self.Handle("Started", self.on_started)
		self.Handle("Stopped", self.on_stopped)
		self.Handle("Closed", self.on_closed)
		self.Handle("ErrorOccured", self.on_error)
		self.Handle("SessionCreated", self.on_session_created)
		self.Handle("SessionRemoved", self.on_session_removed)
		
		self.sessions = {}
		
	def __del__(self):
		dprint("deleting server object")
		
	def DisconnectAll(self, *args):
		for k, v in self.sessions.iteritems():
			v.DisconnectAll()
		self.sessions = {}
		OdsBase.DisconnectAll(self, *args)
		
	def on_started(self):
		self.emit("started")
		
	def on_stopped(self):
		self.emit("stopped")
		
	def on_closed(self):
		self.emit("closed")
		self.DisconnectAll()
		
	def on_error(self, err_name, err_message):
		self.emit("error-occured", err_name, err_message)
		self.DisconnectAll()
		
	def on_session_created(self, path):
		dprint(path)
		self.sessions[path] = OdsServerSession(path)
		self.emit("session-created", self.sessions[path])
		
	def on_session_removed(self, path):
		dprint(path)
		self.emit("session-removed", path)
		self.sessions[path].DisconnectAll()
		del self.sessions[path]
	
	
	
