#!/usr/bin/python

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

from blueman.Constants import *
import gtk
import re

def get_icon(name, size=24):
	ic = gtk.icon_theme_get_default()
	if not ICON_PATH in ic.get_search_path():
		ic.prepend_search_path(ICON_PATH)
		ic.prepend_search_path(ICON_PATH + "/devices")
		ic.prepend_search_path(ICON_PATH + "/signal")
	try:
		icon = ic.load_icon(name, size, 0) 
	except:
		icon = ic.load_icon("bluetooth", size, 0) 

	
	return icon
	
def adapter_path_to_name(path):
	return re.search(".*(hci[0-9]*)", path).groups(0)[0]
