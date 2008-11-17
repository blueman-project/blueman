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
from blueman.bluez.BlueZInterface import BlueZInterface
import dbus
import gobject

class SignalTracker:

	def __init__(self):
		self._signals = []
		
	def Handle(self, *args, **kwargs):
		auto = False

		if not type(args[0]) == str:
			auto = True

		if auto:
			obj = args[0]
			args = args[1:]
			if isinstance(obj, BlueZInterface):
				objtype = "bluez"
				obj.HandleSignal(*args)
			elif isinstance(obj, gobject.GObject):
				objtype = "gobject"
				args = obj.connect(*args)
			elif isinstance(obj, dbus.proxies.Interface):
				objtype = "dbus"
				obj.bus.add_signal_receiver(*args, **kwargs)
		else:
			objtype = args[0]
			obj = args[1]
			args = args[2:]
			if objtype == "bluez":
				obj.HandleSignal(*args)
			elif objtype == "gobject":
				args = obj.connect(*args)
			elif objtype == "dbus":
				obj.bus.add_signal_receiver(*args, **kwargs)

		self._signals.append((objtype, obj, args, kwargs))
		
	def DisconnectAll(self):
		for sig in self._signals:
			
			(objtype, obj, args, kwargs) = sig
			if objtype == "bluez":
				obj.UnHandleSignal(*args, **kwargs)
			elif objtype == "gobject":
				obj.disconnect(args)
			elif objtype == "dbus":
				obj.bus.remove_signal_receiver(*args, **kwargs)
		
		self._signals = []


		
