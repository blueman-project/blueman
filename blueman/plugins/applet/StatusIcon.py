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
import gtk
import gobject

class StatusIcon(AppletPlugin, gtk.StatusIcon):
	__unloadable__ = False
	
	FORCE_SHOW = 2
	SHOW = 1
	FORCE_HIDE = 0

	def on_load(self, applet):
		gtk.StatusIcon.__init__(self)
		self.lines = {}
		self.pixbuf = None
		
		self.connect("size-changed", self.on_status_icon_resized)
		
		self.SetTextLine(0, _("Bluetooth Enabled"))
		
		
		AppletPlugin.add_method(self.on_query_status_icon_visibility)
		AppletPlugin.add_method(self.on_status_icon_pixbuf_ready)
		
	def on_bluetooth_power_state_changed(self, state):
		if state:
			self.SetTextLine(0, _("Bluetooth Enabled"))
		else:
			self.SetTextLine(0, _("Bluetooth Disabled"))
			
		self.Query()
	
	def Query(self):
		if not self.Applet.Manager:
			self.props.visible = False
			return
			
		rets = self.Applet.Plugins.Run("on_query_status_icon_visibility")
		if StatusIcon.FORCE_HIDE in rets:
			if StatusIcon.FORCE_SHOW in rets:
				self.props.visible = True
			else:
				try:
					if self.Applet.Manager.ListAdapters() == []:
						self.props.visible = False
					else:
						self.props.visible = True
				except:
					self.props.visible = False
		else:
			self.props.visible = False
			
	def SetTextLine(self, id, text):
		if text:
			self.lines[id] = text
		else:
			try:
				del self.lines[id]
			except:
				pass
				
		self.update_tooltip()

			
	def update_tooltip(self):
		s = ""
		keys = self.lines.keys()
		keys.sort()
		for k in keys:
			s += self.lines[k] + "\n"
			
		self.props.tooltip_markup = s[:-1]
			
	def IconShouldChange(self):
		self.on_status_icon_resized(self, self.props.size)
		
	def on_adapter_added(self, path):
		self.Query()
		
	def on_adapter_removed(self, path):
		self.Query()
	
	def on_manager_state_changed(self, state):
		self.Query()
		
	def on_status_icon_resized(self, statusicon, size):
		self.pixbuf = get_icon("blueman-tray", size, fallback="blueman")
		
		def callback(inst, ret):
			if isinstance(ret, gtk.gdk.Pixbuf):
				self.pixbuf = ret
				return (self.pixbuf,)
				
		self.Applet.Plugins.RunEx("on_status_icon_pixbuf_ready", callback, self.pixbuf)

		self.set_from_pixbuf(self.pixbuf)
		return True
		
	def on_query_status_icon_visibility(self):
		return StatusIcon.SHOW
		
	def on_status_icon_pixbuf_ready(self, pixbuf):
		return False

