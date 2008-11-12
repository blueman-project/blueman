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

class SignalTracker:

	def __init__(self):
		self.__signals = []
		
	def Handle(self, type, obj, *args, **kwargs):
		if type == "bluez":
			obj.HandleSignal(*args)
		elif type == "gobject":
			args = obj.connect(*args)
		elif type == "dbus":
			obj.bus.add_signal_receiver(*args, **kwargs)
			
		self.__signals.append((type, obj, args, kwargs))
		
	def DisconnectAll(self):
		for sig in self.__signals:
			(type, obj, args, kwargs) = sig
			if type == "bluez":
				obj.UnHandleSignal(*args, **kwargs)
			elif type == "gobject":
				obj.disconnect(args)
			elif type == "dbus":
				obj.bus.remove_signal_receiver(*args, **kwargs)
		
		self.__signals = []

