
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
import dbus
import dbus.glib
import dbus.service
import inspect

class MethodAlreadyExists(Exception):
	pass
	
class DbusService(dbus.service.Object):
	def __init__(self, interface, path, bus=dbus.SessionBus):
		self.interface = interface
		self.path = path
		
		self.bus = bus()
		self.bus.request_name(self.interface)
		
		dbus.service.Object.__init__(self, self.bus, self.path)
		
	def add_method(self, func, dbus_interface=None, in_signature="", *args, **kwargs):
		if not dbus_interface:
			dbus_interface = self.interface
		
		name = func.__name__	

		if name in self.__class__.__dict__:
			raise MethodAlreadyExists
		
		cnt = 0
		a = inspect.getargspec(func)[0]
		a = ",".join(a[1:])

		#print name, a	
		exec \
"""def %(0)s(self, %(1)s):
	return self.%(0)s._orig_func(%(1)s)

		
%(0)s._orig_func = func
dec = dbus.service.method(dbus_interface, in_signature, *args, **kwargs)(%(0)s)""" % {"0": func.__name__, "1": a}

		
		setattr(self.__class__, name, dec)
		if not dbus_interface in self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__]:
			self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][dbus_interface] = {}
		
		self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][dbus_interface][name] = dec
	
	def add_signal(self, name, dbus_interface=None, signature="", *args, **kwargs):
		if not dbus_interface:
			dbus_interface = self.interface
		
		if name in self.__class__.__dict__:
			raise MethodAlreadyExists
		a = ""
		for i in range(len(dbus.Signature(signature))):
			a += ", arg%d" % i

		exec "def func(self%s): pass" % a
		func.__name__ = name

		dec = dbus.service.signal(dbus_interface, signature, *args, **kwargs)(func)
		setattr(self.__class__, func.__name__, dec)
		if not dbus_interface in self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__]:
			self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][dbus_interface] = {}
		self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][dbus_interface][func.__name__] = dec

		return getattr(self, func.__name__)
		
	def remove_registration(self, name):
		print "remove", name
		delattr(self.__class__, name)
		del self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][self.interface][name]	

