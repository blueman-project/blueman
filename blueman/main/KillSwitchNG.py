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
import dbus
import os
import struct
import weakref
import errno
import gobject
from blueman.main.Mechanism import Mechanism
from blueman.Functions import dprint

class RFKillType:
	ALL       = 	0
	WLAN      = 	1
	BLUETOOTH = 	2
	UWB       = 	3 
	WIMAX     = 	4
	WWAN      = 	5
	GPS       = 	6

class RFKillOp:
	ADD        =	0
	DEL        =	1
	CHANGE     =	2
	CHANGE_ALL = 	3
	
class RFKillState:
	SOFT_BLOCKED =	0
	UNBLOCKED    =	1
	HARD_BLOCKED =	2

RFKILL_EVENT_SIZE_V1 =	8

class Switch:
	def __init__(self, idx, type, soft, hard):
		self.idx = idx
		self.type = type
		self.soft = soft
		self.hard = hard

class KillSwitchNG(gobject.GObject):
	__gsignals__ = {
		'switch-changed' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'switch-added' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'switch-removed' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
	}
	def __init__(self):
		gobject.GObject.__init__(self)
		self.state = True
		self.switches = {}
		try:
			self.fd = os.open("/dev/rfkill", os.O_RDWR | os.O_NONBLOCK)
		except OSError, e:
			if e.errno == errno.EACCES:
				self.fd = os.open("/dev/rfkill", os.O_RDONLY | os.O_NONBLOCK)
			else:
				raise e

		ref = weakref.ref(self)
		self.iom = gobject.io_add_watch(self.fd, gobject.IO_IN | gobject.IO_ERR | gobject.IO_HUP, lambda *args: ref() and ref().io_event(*args) )
		
	def __del__(self):
		try:
			gobject.source_remove(self.iom)
			os.close(self.fd)
		except:
			pass
		
		
	def io_event(self, source, condition):
		if condition & gobject.IO_ERR or condition & gobject.IO_HUP:
			return False
		
		data = os.read(self.fd, RFKILL_EVENT_SIZE_V1)
		if len(data) != RFKILL_EVENT_SIZE_V1:
			dprint("Bad rfkill event size")
		else:
			(idx, type, op, soft, hard) = struct.unpack("IBBBB", data)
			
			if op == RFKillOp.ADD:
				self.switches[idx] = Switch(idx, type, soft, hard)
				self.emit("switch-added", self.switches[idx])
			elif op == RFKillOp.DEL:
				self.emit("switch-removed", self.switches[idx])
				del self.switches[idx]
			elif op == RFKillOp.CHANGE:
				self.switches[idx].type = type
				self.switches[idx].soft = soft
				self.switches[idx].hard = hard
				self.emit("switch-changed", self.switches[idx])
		
		return True
		
		
	def SetGlobalState(self, state):
		dprint("set", state)
		#if we have permission, we just send an event, else we use the dbus interface				
		try:
			event = struct.pack("IBBBB", 0, RFKillType.BLUETOOTH, RFKillOp.CHANGE_ALL, (0 if state else 1), 0)
			os.write(self.fd, event)
		except:	
			m = Mechanism()
			m.SetRfkillState(state)
			

		
	def GetGlobalState(self):
		self.state = True
		for s in self.switches.itervalues():
			if s.type == RFKillType.BLUETOOTH:
				self.state &= (s.soft == 0 and s.hard == 0)
				
		dprint(self.state)
		return self.state
		
