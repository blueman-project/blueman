# Copyright (C) 2009 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2009 Tadas Dailyda <tadas at dailyda dot com>
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

from blueman.plugins.ConfigPlugin import ConfigPlugin
from blueman.main.SignalTracker import SignalTracker
import cPickle as pickle
import os
import atexit
import dbus.service, dbus.glib
import weakref
import signal
import glib
import copy

def sighandler():
	print "got signal"
	exit()

signal.signal(signal.SIGTERM, sighandler)
signal.signal(signal.SIGHUP, sighandler)

dbus.service.Object.SUPPORTS_MULTIPLE_OBJECT_PATHS = True

cfg_path = os.path.expanduser('~/.config/blueman/blueman.cfg')

class Monitor(dbus.service.Object):
	__id__ = 0
	def __init__(self, plugin):
		Monitor.__id__ += 1
		self.inst_id = "/inst%d" % Monitor.__id__

		self.plugin = plugin
		self.sigs = SignalTracker()
		self.bus = dbus.SessionBus();
		
		dbus.service.Object.__init__(self)
		self.add_to_connection(self.bus, self.inst_id)
		
		self.sigs.Handle("dbus", self.bus, self.on_value_changed, "ValueChanged", "org.blueman.Config")
		
	def on_value_changed(self, section, data):
		s = "".join(chr(b) for b in data)

		(key, value) = pickle.loads(s)
			
		key = str(key)
		
		if self.plugin().section == section:
			self.plugin().set(key, value, True)
		else:
			if not section in File.__db__:
				File.__db__[section] = {}
	
			File.__db__[section][key] = value
		
	@dbus.service.signal(dbus_interface="org.blueman.Config", signature='say')
	def ValueChanged(self, section, data):
		pass

class File(ConfigPlugin):
	__priority__ = 1
	__plugin__ = "file"
	
	__db__ = None
	
	timeout = None

	def __del__(self):
		self.Monitor.sigs.DisconnectAll()
		self.Monitor.remove_from_connection()
		del self.Monitor

	def on_load(self, section):
		
		if not File.__db__:
			if not os.path.exists(os.path.expanduser('~/.config/blueman')):
				try:
					os.makedirs(os.path.expanduser('~/.config/blueman'))
				except:
					pass
			try:
				f = open(cfg_path, "r")
				File.__db__ = pickle.load(f)
				f.close()
			except Exception, e:
				File.__db__ = {}

			atexit.register(File.save)

		
		self.config = File.__db__
		self.section = section
		if self.section == "":
			self.section = "__blueman__"
		
		if not self.section in self.config:
			self.config[self.section] = {}
			
		self.Monitor = Monitor(weakref.ref(self))
	
	@staticmethod	
	def save():
		dprint("Saving config")
		f = open(cfg_path, "w")
		pickle.dump(File.__db__, f, pickle.HIGHEST_PROTOCOL)
		f.close()
		File.timeout = None

	
	def set(self, key, value, local=False):
		
		if key in self.config[self.section]:
			prev = self.config[self.section][key]
		else:
			prev = None
		
		if prev != value:
			self.config[self.section][key] = copy.deepcopy(value)
			self.emit("property-changed", key, value)
			
			if not local:
				if File.timeout:
					glib.source_remove(File.timeout)
				File.timeout = glib.timeout_add(1000, File.save)
				self.Monitor.ValueChanged(self.section, pickle.dumps((key, value), pickle.HIGHEST_PROTOCOL))
		
	def get(self, key):
		if key in self.config[self.section]:
			return copy.deepcopy(self.config[self.section][key])
		else:
			return None
			
	def list_dirs(self):
		l = []
		for key in self.config.iterkeys():
			if self.section in key:
				k = key.replace(self.section, "")
				s = k.split("/")
				if len(s) > 1:
					l.append(self.section + "/" + s[1])
		return l
