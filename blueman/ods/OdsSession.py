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

class OdsSession(OdsBase):
	__gsignals__ = {
		'connected' : (GObject.SignalFlags.RUN_FIRST, None, ()),
		'cancelled' : (GObject.SignalFlags.NO_HOOKS, None, ()),
		'disconnected' : (GObject.SignalFlags.NO_HOOKS, None, ()),
		'transfer-started' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
		'transfer-progress' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT,)),
		'transfer-completed' : (GObject.SignalFlags.NO_HOOKS, None, ()),
		'error-occurred' : (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
	}
	
	def __init__(self, obj_path):
		OdsBase.__init__(self, "org.openobex.Session", obj_path)
		self.Connected = False
		self.Handle("Cancelled", self.on_cancelled)
		self.Handle("Disconnected", self.on_disconnected)
		self.Handle("TransferStarted", self.on_trans_started)
		self.Handle("TransferProgress", self.on_trans_progress)
		self.Handle("TransferCompleted", self.on_trans_complete)
		self.Handle("ErrorOccurred", self.on_error)
		
	def __del__(self):
		dprint("deleting session")
		
	#this is executed by gobject, before the connected signal is emitted
	def do_connected(self):
		self.Connected = True
		
	def on_cancelled(self):
		self.emit("cancelled")
		#self.DisconnectAll()
		
	def on_disconnected(self):
		dprint("disconnected")
		self.Connected = False
		self.emit("disconnected")
		#self.DisconnectAll()
		
	def on_trans_started(self, filename, path, size):
		self.emit("transfer-started", filename, path, size)
		
	def on_trans_progress(self, bytes):
		self.emit("transfer-progress", bytes)
		
	def on_trans_complete(self):
		self.emit("transfer-completed")
		
	def on_error(self, name, msg):
		self.emit("error-occurred", name, msg)
		#self.DisconnectAll()
