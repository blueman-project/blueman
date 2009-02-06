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

import gtk
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget
import gettext

_ = gettext.gettext


class DeviceSelectorDialog(gtk.Dialog):
	
	

	def __init__(self, title=_("Select Device"), parent=None, discover=True):

		gtk.Dialog.__init__(self, title, parent, 0, (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
						 	     gtk.STOCK_OK,     gtk.RESPONSE_ACCEPT))
		
		
		self.props.resizable = False
		self.props.icon_name = "blueman"
		self.selector = DeviceSelectorWidget()
		self.selector.show()
		
		#self.selector.destroy()
		#self.selector = None
		
		align = gtk.Alignment(0.5,0.5,1.0,1.0)
		align.add(self.selector)
		
		align.set_padding(5,5,5,5)
		align.show()
		self.vbox.pack_start(align)
		
		
		#(adapter, device)
		self.selection = None
		
		self.selector.List.connect("device-selected", self.on_device_selected)
		self.selector.List.connect("adapter-changed", self.on_adapter_changed)
		if discover:
			self.selector.List.DiscoverDevices()
		
		self.selector.List.connect("row-activated", self.on_row_activated)
		
	def on_row_activated(self, treeview, path, view_column, *args):
		self.response(gtk.RESPONSE_ACCEPT)
		
	def on_adapter_changed(self, devlist, adapter):
		self.selection = None
		
	def on_device_selected(self, devlist, device, iter):
		self.selection = (devlist.Adapter.GetObjectPath(), device)
		
	def GetSelection(self):
		if self.selection:
			return (self.selection[0], self.selection[1].Copy())
		else:
			return None
		

