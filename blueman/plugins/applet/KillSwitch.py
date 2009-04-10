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
from blueman.Functions import _

from blueman.main.SignalTracker import SignalTracker
from blueman.plugins.AppletPlugin import AppletPlugin
import blueman.main.KillSwitch as _KillSwitch

class KillSwitch(AppletPlugin):
	__author__ = "Walmis"
	__autoload__ = False
	__description__ = _("Toggles a Bluetooth killswitch when Bluetooth power state changes. Some laptops, mostly Dells have this feature")
	__depends__ = ["PowerManager", "StatusIcon"]
	__icon__ = "system-shutdown"
	
	def on_load(self, applet):
		self.Manager = _KillSwitch.Manager()
		
	def on_unload(self):
		pass
		
	def on_bluetooth_power_state_changed(self, state):
		self.Manager.SetGlobalState(state)
		
	def on_query_status_icon_visibility(self):
		if self.Manager.GetGlobalState():
			return 1 #StatusIcon.SHOW
		else:
			#if killswitch removes the bluetooth adapter, dont hide the statusicon,
			#so that the user could turn bluetooth back on.
			return 2 #StatusIcon.FORCE_SHOW
		
