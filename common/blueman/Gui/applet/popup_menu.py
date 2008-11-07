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

import sys

sys.path = ["../common/"] + sys.path

from blueman.constants import *
import gettext
_ = gettext.gettext

import gtk

class popup_menu:

	def __init__(self, status_icon):
		status_icon.connect('popup-menu', self.on_popup_menu)
		
		menu_items = []
		menu_items += [gtk.MenuItem(_('Setup new device')+'...', False)]
		menu_items += [gtk.MenuItem(_('Send files to device')+'...', False)]
		if OBEX_BROWSE_AVAILABLE:
			menu_items += [gtk.MenuItem(_('Browse files on device')+'...', False)]
		menu_items += [gtk.SeparatorMenuItem()]
		menu_items += [gtk.MenuItem(_('Devices')+'...', False)]
		menu_items += [gtk.MenuItem(_('Adapters')+'...', False)]
		menu_items += [gtk.MenuItem(_('Local services')+'...', False)]
		menu_items += [gtk.SeparatorMenuItem()]
		menu_items += [gtk.ImageMenuItem(gtk.STOCK_ABOUT)]
		
		self.menu = gtk.Menu()
		for menu_item in menu_items:
			self.menu.append(menu_item)
			menu_item.show()
	
	def on_popup_menu(self, status_icon, button, activate_time):
		self.menu.popup(None, None, gtk.status_icon_position_menu,
						button, activate_time, status_icon)
		
