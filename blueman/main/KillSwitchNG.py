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
from gi.repository import GObject
from blueman.main.Mechanism import Mechanism
from blueman.Functions import dprint
import stat

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

class KillSwitchNG(GObject.GObject):
	__gsignals__ = {
		'switch-changed' : (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
		'switch-added' : (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
		'switch-removed' : (GObject.SignalFlags.RUN_FIRST, None, (GObject.TYPE_PYOBJECT,)),
	}
	def __init__(self):
		GObject.GObject.__init__(self)
		self.state = True
		self.hardblocked = False
		
		self.switches = {}

		mode = os.stat("/dev/rfkill").st_mode
		
		flags = 0
		if os.getuid() == 0:
			flags = os.O_RDWR
		else:
			if (mode & stat.S_IWOTH) == 0:
				flags = os.O_RDONLY
			else:
				flags = os.O_RDWR
		
			if (mode & stat.S_IROTH) == 0:
				m = Mechanism()
				m.DevRfkillChmod()
		
			
		flags |= os.O_NONBLOCK
		
		self.fd = os.open("/dev/rfkill", flags)

		ref = weakref.ref(self)
		self.iom = GObject.io_add_watch(self.fd, GObject.IO_IN | GObject.IO_ERR | GObject.IO_HUP, lambda *args: ref() and ref().io_event(*args) )
		
	def __del__(self):
		try:
			GObject.source_remove(self.iom)
			os.close(self.fd)
		except:
			pass
			
	@property		
	def devices(self):
		def m(x):
			if x.type == RFKillType.BLUETOOTH:
				return x
		stuff = map(m, self.switches.values())
		stuff = filter(lambda x: x is not None, stuff)

		return stuff
		
	def io_event(self, source, condition):
		if condition & GObject.IO_ERR or condition & GObject.IO_HUP:
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
				sw = self.switches[idx]
				del self.switches[idx]
				self.emit("switch-removed", sw)
			elif op == RFKillOp.CHANGE:
				orig_soft = self.switches[idx].soft
				orig_hard = self.switches[idx].hard
				
				if orig_soft != soft or orig_hard != hard:
					self.switches[idx].type = type
					self.switches[idx].soft = soft
					self.switches[idx].hard = hard
					self.emit("switch-changed", self.switches[idx])
					
		return True
		
	def do_switch_added(self, switch):
		if switch.type == RFKillType.BLUETOOTH:
			self.update_state()
	
	def do_switch_changed(self, switch):
		if switch.type == RFKillType.BLUETOOTH:
			self.update_state()
			
	def do_switch_removed(self, switch):
		if switch.type == RFKillType.BLUETOOTH:
			self.update_state()		
		
		
	def SetGlobalState(self, state, **kwargs):
		dprint("set", state)
		#if we have permission, we just send an event, else we use the dbus interface				
		if os.getuid() == 0:
			event = struct.pack("IBBBB", 0, RFKillType.BLUETOOTH, RFKillOp.CHANGE_ALL, (0 if state else 1), 0)
			os.write(self.fd, event)
		else:
			m = Mechanism()
			m.SetRfkillState(state, **kwargs)

	def update_state(self):
		self.state = True
		self.hardblocked = False
		for s in self.switches.itervalues():
			if s.type == RFKillType.BLUETOOTH:
				self.hardblocked |= s.hard
				self.state &= (s.soft == 0 and s.hard == 0)
				
		dprint("State:", self.state)

	def GetGlobalState(self):
		return self.state
		
	@property
	def GlobalState(self):
		return self.state
		
	@property
	def HardBlocked(self):
		return self.hardblocked
		
