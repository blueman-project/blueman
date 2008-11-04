#
#
# blueman
# (c) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from blueman.Gui.device_list import device_list
from blueman.Gui.PixbufTable import PixbufTable
from blueman.Gui.CellRendererPixbufTable import CellRendererPixbufTable
from blueman.device_class import get_minor_class

import gtk
from blueman.constants import *


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
	



class main_device_list(device_list):
	
	def __init__(self, adapter=None):
		data = [
			#device picture
			["device_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":0}, None],
			
			#device caption
			["caption", str, gtk.CellRendererText(), {"markup":1}, None, {"expand": True}],

			
			["rssi_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":2}, None, {"spacing": 0}],
			["lq_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":3}, None, {"spacing": 0}],
			["tpl_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":4}, None, {"spacing": 0}],
			
			["bonded_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":5}, None, {"spacing": 0}],
			["trusted_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":6}, None, {"spacing": 0}],
			
			["connected", bool],
			["bonded", bool],
			["trusted", bool],	
			
			["rssi", float],
			["lq", float],
			["tpl", float],

			["svc_icons", 'PyObject', CellRendererPixbufTable(), {"pixbuffs":13}, None]
		
		]
		device_list.__init__(self, adapter, data)
		self.set_headers_visible(False)
		
	
	def level_setup_event(self, iter, device, cinfo):

		return True
	
	def row_setup_event(self, iter, device):
		props = device.GetProperties()
		print props

			
		try:
			klass = get_minor_class(props["Class"])
		except:
			klass = "Unknown"
			

		icon = get_icon("blueman-"+klass, 48)
		
		try:
			self.row_update_event(iter, "Paired", props["Paired"])
		except:
			pass
		try:
			self.row_update_event(iter, "Trusted", props["Trusted"])
		except:
			pass
			
		#tab = PixbufTable()
		#tab.set("audio", get_icon("computer"))

		#self.set(iter, svc_icons=tab)

		name = props["Alias"]
		address = props["Address"]

		caption = "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" % {"0":name, "1":klass.capitalize(), "2":address}
		self.set(iter, caption=caption, device_pb=icon)

	def row_update_event(self, iter, key, value):
		#print iter, key, value
		if key == "Trusted":
			if value:
				self.set(iter, trusted_pb=get_icon("blueman-trust", 48))
			else:
				self.set(iter, trusted_pb=None)
		elif key == "Paired":
			if value:
				self.set(iter, bonded_pb=get_icon("blueman-bond", 48))
			else:
				self.set(iter, bonded_pb=None)
				
	
	def level_setup_event(self, iter, device, cinfo):
		def rnd(value):
			return int(round(value,-1))
		#print self.window.get_state() & gtk.gdk.WINDOW_STATE_ICONIFIED
		if True:
			if cinfo != None:
				rssi = float(cinfo.get_rssi())
				lq = float(cinfo.get_lq())
				tpl = float(cinfo.get_tpl())

				rssi_perc = 50 + (rssi / 127 / 2 * 100)
				tpl_perc = 50 + (tpl / 127 / 2 * 100)
				lq_perc = lq / 255 * 100

				self.set(iter,  rssi_pb=get_icon("blueman-rssi-%s" % rnd(rssi_perc), 48),
						lq_pb=get_icon("blueman-lq-%s" % rnd(lq_perc), 48),
						tpl_pb=get_icon("blueman-tpl-%s" % rnd(tpl_perc), 48))
			else:
				self.set(iter, rssi_pb=None, lq_pb=None, tpl_pb=None)
		else:
			print "invisible"
		#set_signal("rssi", rssi_perc, "/signal/rssi/rssi_", ".png", self.row)
		#set_signal("lq", lq_perc, "/signal/lq/lq_", ".png", self.row)
		#set_signal("tpl", tpl_perc, "/signal/tpl/tpl_", ".png", self.row)
			

