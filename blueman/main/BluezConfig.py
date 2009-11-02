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

from blueman.iniparse.compat import SafeConfigParser

class BluezConfig(SafeConfigParser):
	def __init__(self, filename):
		SafeConfigParser.__init__(self)
		
		self.filename = filename
		
		self.path = "/etc/bluetooth/%s" % filename
		
		self.read(self.path)
		
	def write(self):
		f = open(self.path, "wb")
		SafeConfigParser.write(self, f)
