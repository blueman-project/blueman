
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

import gtk
from blueman.Functions import dprint
from blueman.main.PolicyKitAuth import PolicyKitAuth
from blueman.main.Mechanism import Mechanism

from blueman.bluez.Adapter import Adapter
from blueman.main.applet.BluezAgent import TempAgent
from blueman.main.Device import Device



class MethodAlreadyExists(Exception):
	pass
	
class DbusService(dbus.service.Object):
	def __init__(self, applet):
		self.applet = applet
		self.bus = dbus.SessionBus();
		self.bus.request_name("org.blueman.Applet")
		
		
		dbus.service.Object.__init__(self, self.bus, "/")
		
	def add_method(self, func, dbus_interface='org.blueman.Applet', in_signature="", *args, **kwargs):
		name = func.__name__	
		
		if name in self.__class__.__dict__:
			raise MethodAlreadyExists
		
		cnt = 0
		a = ""
		for z in dbus.Signature(in_signature):
			a += "arg%d," % cnt
			cnt+= 1
			
		a = a[0:-1]
		
		if "async_callbacks" in kwargs:
			a += ","
			a += kwargs["async_callbacks"][0]
			a += ","
			a += kwargs["async_callbacks"][1]
			
		exec \
"""def %(0)s(self, %(1)s):
	return self.%(0)s._orig_func(%(1)s)

		
%(0)s._orig_func = func
dec = dbus.service.method(dbus_interface, in_signature, *args, **kwargs)(%(0)s)""" % {"0": func.__name__, "1": a}

		
		setattr(self.__class__, name, dec)
		self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][dbus_interface][name] = dec
	
	def add_signal(self, name, dbus_interface='org.blueman.Applet', signature="", *args, **kwargs):
		if name in self.__class__.__dict__:
			raise MethodAlreadyExists
		a = ""
		for i in range(len(dbus.Signature(signature))):
			a += ", arg%d" % i

		exec "def func(self%s): pass" % a
		func.__name__ = name

		dec = dbus.service.signal(dbus_interface, signature, *args, **kwargs)(func)
		setattr(self.__class__, func.__name__, dec)
		self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__][dbus_interface][func.__name__] = dec

		return getattr(self, func.__name__)
		
	def remove_registration(self, name):
		print "remove", name
		delattr(self.__class__, name)
		del self._dbus_class_table[self.__class__.__module__+"."+self.__class__.__name__]['org.blueman.Applet'][name]	
		
		


		
		
	#in: interface name
	@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="s", out_signature="")
	def DhcpClient(self, interface):
		self.applet.NM.dhcp_acquire(interface)
		
	

		
	
	
	
		
