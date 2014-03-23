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
from gi.repository import Gtk
from blueman.plugins.AppletPlugin import AppletPlugin

class ExitItem(AppletPlugin):
	__depends__ = ["Menu"]
	__autoload__ = False
	__description__ = _("Adds an exit menu item to quit the applet")
	__author__ = "Walmis"
	__icon__ = "gtk-quit"
	
	def on_load(self, applet):
		item = Gtk.ImageMenuItem.new_from_stock(Gtk.STOCK_QUIT, None)
		item.connect("activate", lambda x: Gtk.main_quit())
		applet.Plugins.Menu.Register(self, item, 100)
		
	def on_unload(self):
		self.Applet.Plugins.Menu.Unregister(self)
