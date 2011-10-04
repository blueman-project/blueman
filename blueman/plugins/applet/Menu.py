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
from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin

import gobject
import gtk

class Menu(AppletPlugin):
	__depends__ = ["StatusIcon"]
	__description__ = _("Provides a menu for the applet and an API for other plugins to manipulate it")
	__icon__ = "menu-editor"
	__author__ = "Walmis"
	__unloadable__ = False
	
	def on_load(self, applet):
		self.Applet = applet
		
		self.Applet.Plugins.StatusIcon.connect("popup-menu", self.on_popup_menu)
		
		self.__plugins_loaded = False
		
		self.__menuitems = []
		self.__menu = gtk.Menu()
		
	def on_popup_menu(self, status_icon, button, activate_time):
		self.__menu.popup(None, None, gtk.status_icon_position_menu,
						button, activate_time, status_icon)		
	
	def __sort(self):
		self.__menuitems.sort(lambda a, b: cmp(a[0], b[0]))
		
	def __clear(self):
		def each(child):
			self.__menu.remove(child)
		self.__menu.foreach(each)	
	
	def __load_items(self):
		for item in self.__menuitems:
			self.__menu.append(item[1])
			if item[2]:
				item[1].show()		
	
	def Register(self, owner, item, priority, show=True):
		self.__menuitems.append((priority, item, show, owner))
		if self.__plugins_loaded:
			self.__sort()
			self.__clear()
			self.__load_items()
			
		
	def Unregister(self, owner):
		for i in reversed(self.__menuitems):
			priority, item, show, orig_owner = i
			if orig_owner == owner:
				self.__menu.remove(item)
				self.__menuitems.remove(i)
		
	def on_plugins_loaded(self):
		self.__plugins_loaded = True
		self.__sort()
		self.__load_items()
		
	def get_menu(self):
		return self.__menu
		
			

