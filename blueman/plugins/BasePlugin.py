# Copyright (C) 2010 Valmantas Paliksa <walmis at balticum-tv dot lt>
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

import traceback

class MethodAlreadyExists(Exception):
	pass

class BasePlugin(object):
	__depends__ = []
	__conflicts__ = []
	__priority__ = 0
	
	__description__ = None
	__author__ = None
	
	__unloadable__ = True
	__autoload__ = True
	
	__instance__ = None
	
	def __init__(self, parent):
		self.__parent__ = parent
		
		self.__methods = []
		
	def __del__(self):
		print "Deleting plugin instance", self
		
	
	@classmethod
	def add_method(cls, func):
		func.im_self.__methods.append((cls, func.__name__))

		if func.__name__ in cls.__dict__:
			raise MethodAlreadyExists
		else:
			setattr(cls, func.__name__, func)	
	
	def _unload(self):
		self.on_unload()

		for cls, met in self.__methods:
			delattr(cls, met)
			
		self.__class__.__instance__ = None
	
	def _load(self, parent):
		try:
			self.on_load(parent)
			#self.on_manager_state_changed(applet.Manager != None)
			self.__class__.__instance__ = self
		except Exception, e:
			#AppletPlugin.instances.remove(self)
			self.__class__.__instance__ = None
			traceback.print_exc()
			raise
			
	#virtual methods
	def on_load(self, applet):
		pass
	
	def on_unload(self):
		raise NotImplementedError
