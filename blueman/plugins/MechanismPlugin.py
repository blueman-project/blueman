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

class MechanismPlugin(object):
	
	def __init__(self, mechanism):
		self.m = mechanism
		self.timer = self.m.timer
		
		self.confirm_authorization = self.m.confirm_authorization
		
		self.on_load()

	def add_dbus_method(self, func, *args, **kwargs):
		self.m.add_method(func, *args, **kwargs)

	def add_dbus_signal(self, func, *args, **kwargs):
		self.m.add_signal(func, *args, **kwargs)
		
	def check_auth(self, id, caller):
		self.m.confirm_authorization(id, caller)
		
	def on_load(self):
		pass
