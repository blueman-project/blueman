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
# NMMonitor: Monitors a selected device and emits a signal when it was disconnected via NetworkManager
import gobject
import dbus
from blueman.Functions import *

from blueman.main.SignalTracker import SignalTracker
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.KillSwitchNG import KillSwitchNG, RFKillType, RFKillState
try:
	import blueman.main.KillSwitch as _KillSwitch
except:
	pass
	
class KillSwitch(AppletPlugin):
	__author__ = "Walmis"
	__description__ = _("Toggles a Bluetooth killswitch when Bluetooth power state changes. Some laptops, mostly Dells have this feature\n<b>Note</b>: This plugin stays on automatically if it detects a killswitch.")
	__depends__ = ["PowerManager", "StatusIcon"]
	__icon__ = "system-shutdown"
	__options__  = {
		"checked" : (bool, False)
	}
	
	def on_load(self, applet):
		self.signals = SignalTracker()

		try:
			self.Manager = KillSwitchNG()
			self.signals.Handle(self.Manager, "switch-changed", self.on_switch_changed)
			dprint("Using the new killswitch system")
		except OSError, e:
			dprint("Using the old killswitch system, reason:", e)
			try:
				self.Manager = _KillSwitch.Manager()
			except:
				raise Exception("Failed to initialize killswitch manager")
				
		
			if not self.get_option("checked"):
				gobject.timeout_add(1000, self.check)
				
		self.signals.Handle(self.Manager, "switch-added", self.on_switch_added)
		self.signals.Handle(self.Manager, "switch-removed", self.on_switch_removed)		

	def on_switch_added(self, manager, switch):
		if switch.type == RFKillType.BLUETOOTH:
			dprint("killswitch registered", switch.idx)
#			if manager.HardBlocked:
#				self.Applet.Plugins.PowerManager.SetPowerChangeable(False)
#			
#			if not self.Manager.GetGlobalState():	
#				self.Applet.Plugins.PowerManager.SetBluetoothStatus(False)
#			
#			pm_state = self.Applet.Plugins.PowerManager.GetBluetoothStatus()
#			if self.Manager.GetGlobalState() != pm_state:
#				self.Manager.SetGlobalState(pm_state)
		
				
	def on_switch_changed(self, manager, switch):
		if switch.type == RFKillType.BLUETOOTH:
			s = manager.GetGlobalState()
			dprint("Global state:", s, "\nswitch.soft:", switch.soft, "\nswitch.hard:", switch.hard)
			self.Applet.Plugins.PowerManager.UpdatePowerState()

			self.Applet.Plugins.StatusIcon.Query()
			
	def on_switch_removed(self, manager, switch):
		if switch.type == RFKillType.BLUETOOTH:
			if len(manager.devices) == 0:
				self.Applet.Plugins.StatusIcon.Query()
				
	def on_power_state_query(self, manager):
		if self.Manager.HardBlocked:
			return manager.STATE_OFF_FORCED
		else:
			dprint(self.Manager.GetGlobalState())
			if self.Manager.GetGlobalState():
				return manager.STATE_ON
			else:
				return manager.STATE_OFF
		
			
	def check(self):
		try:
			if len(self.Manager.devices) == 0:
				self.set_option("checked", True)
				#this machine does not support bluetooth killswitch, let's unload
				self.Applet.Plugins.SetConfig("KillSwitch", False)
		except:
			pass	
			
	def on_power_state_change_requested(self, manager, state, cb):
		dprint(state)
		def reply(*args):
			cb(True)
			
		def error(*args):
			cb(False)
		
		if not self.Manager.HardBlocked:
			self.Manager.SetGlobalState(state, reply_handler=reply, error_handler=error)
		else:
			cb(True)			

	def on_unload(self):
		self.signals.DisconnectAll()
		
	def on_query_status_icon_visibility(self):
		if self.Manager.HardBlocked:
			return 1
		
		state = self.Manager.GetGlobalState()
		if state:
			if isinstance(self.Manager, KillSwitchNG) and len(self.Manager.devices) > 0:
				return 2
			
			return 1 #StatusIcon.SHOW
		elif len(self.Manager.devices) > 0 and not state:
			#if killswitch removes the bluetooth adapter, dont hide the statusicon,
			#so that the user could turn bluetooth back on.
			return 2 #StatusIcon.FORCE_SHOW
			
		return 1
		
