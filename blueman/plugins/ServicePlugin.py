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

class ServicePlugin(object):
	instances = []
	__plugin_info__ = None
	
	def __init__(self, services_inst):
		ServicePlugin.instances.append(self)
		self._options = []
		self._orig_state = {}
		self.__services_inst = services_inst
		
		self.__is_exposed = False
		self._is_loaded = False
		
	def _on_enter(self):
		if not self.__is_exposed:
			self.on_enter()
			self.__is_exposed = True
			
	def _on_leave(self):
		if self.__is_exposed:
			self.on_leave()
			self.__is_exposed = False

	
	#call when option has changed.
	def option_changed_notify(self, option_id, state=True):

		if not option_id in self._options:
			self._options.append(option_id)
		else:
			if state:
				self._options.remove(option_id)

		
		self.__services_inst.option_changed()
	
	def get_options(self):
		return self._options
		
	def clear_options(self):
		self._options = []


	#virtual functions
	#in: container hbox
	#out: (menu entry name, menu icon name)
	def on_load(self, container):
		pass
	
	def on_unload(self):
		pass
	
	#return true if apply button should be sensitive or false if not. -1 to force disabled
	def on_query_apply_state(self):
		pass
		
	def on_apply(self):
		pass
	
	#called when current plugin's page is selected. The plugin's widget should be shown
	def on_enter(self):
		pass
	
	#called when current plugin's page is changed to another. The plugin's widget should be hidden.
	def on_leave(self):
		pass
