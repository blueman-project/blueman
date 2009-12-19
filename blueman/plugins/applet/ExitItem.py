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
import gtk
from blueman.plugins.AppletPlugin import AppletPlugin

class ExitItem(AppletPlugin):
	__depends__ = ["Menu"]
	__autoload__ = False
	__description__ = _("Adds an exit menu item to quit the applet")
	__author__ = "Walmis"
	__icon__ = "gtk-quit"
	
	def on_load(self, applet):
		item = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		item.connect("activate", lambda x: gtk.main_quit())
		applet.Plugins.Menu.Register(self, item, 100)
		
	def on_unload(self):
		self.Applet.Plugins.Menu.Unregister(self)
