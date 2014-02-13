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

from gi.repository import GObject
import os
from blueman.Functions import dprint

import blueman.plugins.config
from blueman.plugins.ConfigPlugin import ConfigPlugin

print "Loading configuration plugins"

path = os.path.dirname(blueman.plugins.config.__file__)
plugins = []
for root, dirs, files in os.walk(path):
	for f in files:
		if f.endswith(".py") and not (f.endswith(".pyc") or f.endswith("_.py")):
			plugins.append(f[0:-3])

for plugin in plugins:
	try:
		__import__("blueman.plugins.config.%s" % plugin, None, None, [])
	except ImportError, e:
		dprint("Skipping plugin %s\n%s" % (plugin, e))

def compare(a, b):
	return cmp(a.__priority__, b.__priority__)

class Config(object):
	def __new__(c, section=""):
		classes = ConfigPlugin.__subclasses__()
		classes.sort(compare)
		
		for cls in classes:
			try:
				inst = cls(section)
				print "Using %s config backend" % cls.__plugin__
				return inst
			except Exception, e:
				print "Skipping plugin", cls.__plugin__
				print e
			
			print "No suitable configuration backend found, exitting"
			exit(1)
