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

class OdsServer(OdsBase):
	__gsignals__ = {
		'started' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'stopped' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'closed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
		'error-occured' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		'session-created' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'session-removed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
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
		self.sessions[path] = OdsServerSession(path)
		self.emit("session-created", path)
		
	def on_session_removed(self, path):
		self.emit("session-removed", path)
	
	
	
