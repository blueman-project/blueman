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
from blueman.Functions import _
from blueman.plugins.AppletPlugin import AppletPlugin
import gtk
import gobject

class StatusIcon(AppletPlugin, gtk.StatusIcon):
	__unloadable__ = False
	
	FORCE_SHOW = 2
	SHOW = 1
	FORCE_HIDE = 0

	def on_load(self, applet):
		gtk.StatusIcon.__init__(self)
		self.Applet = applet
		
		self.pixbuf = None
		
		self.connect("size-changed", self.on_status_icon_resized)
		
		self.set_tooltip(_("Bluetooth applet"))
		
		AppletPlugin.add_method(self.on_query_status_icon_visibility)
		AppletPlugin.add_method(self.on_status_icon_pixbuf_ready)
	
	def Query(self):
		rets = self.Applet.Plugins.Run("on_query_status_icon_visibility")

		if not StatusIcon.FORCE_SHOW in rets:
			if StatusIcon.FORCE_HIDE in rets:
				self.props.visible = False
			else:
				if not self.Applet.Manager:
					self.props.visible = False
				else:
					try:
						if self.Applet.Manager.ListAdapters() == []:
							self.props.visible = False
						else:
							self.props.visible = True
					except:
						self.props.visible = False
		else:
			self.props.visible = True
		
	def on_adapter_added(self, path):
		self.Query()
		
	def on_adapter_removed(self, path):
		self.Query()
	
	def on_manager_state_changed(self, state):
		self.Query()
		
	def on_status_icon_resized(self, statusicon, size):
		self.pixbuf = get_icon("blueman", size)

		ret = self.Applet.Plugins.Run("on_status_icon_pixbuf_ready", self.pixbuf)
		if True in ret:
			return True
		self.set_from_pixbuf( self.pixbuf )
		return True
		
	def on_query_status_icon_visibility(self):
		return StatusIcon.SHOW
		
	def on_status_icon_pixbuf_ready(self, pixbuf):
		return False

