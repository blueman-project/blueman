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

from blueman.gui.DeviceList import DeviceList
from blueman.gui.PixbufTable import PixbufTable
from blueman.gui.CellRendererPixbufTable import CellRendererPixbufTable
from blueman.DeviceClass import get_minor_class

import gtk
from blueman.Constants import *
from blueman.Functions import *


import gettext
_ = gettext.gettext

class ManagerDeviceList(DeviceList):
	
	def __init__(self, adapter=None):
		data = [
			#device picture
			["device_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":0}, None],
			
			#device caption
			["caption", str, gtk.CellRendererText(), {"markup":1}, None, {"expand": True}],

			
			["rssi_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":2}, None, {"spacing": 0}],
			["lq_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":3}, None, {"spacing": 0}],
			["tpl_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":4}, None, {"spacing": 0}],
			
			#trusted/bonded icons
			#["tb_icons", 'PyObject', CellRendererPixbufTable(), {"pixbuffs":5}, None],
			
			["connected", bool], #used for quick access instead of device.GetProperties
			["bonded", bool], #used for quick access instead of device.GetProperties
			["trusted", bool], #used for quick access instead of device.GetProperties	
			["fake", bool], #used for quick access instead of device.GetProperties, 
					#fake determines whether device is "discovered" or a real bluez device
			
			["rssi", float],
			["lq", float],
			["tpl", float],
			["orig_icon", 'GdkPixbuf']

			
		
		]
		DeviceList.__init__(self, adapter, data)
		self.set_headers_visible(False)
		self.props.has_tooltip = True
		
		self.connect("query-tooltip", self.tooltip_query)		
		self.tooltip_row = -1
		self.tooltip_col = None
		
	
	def get_device_icon(self, klass):
		return get_icon("blueman-"+klass.replace(" ", "-").lower(), 48)
	
	
	def device_add_event(self, device):
		if device.Fake:
			self.PrependDevice(device)
		else:
			self.AppendDevice(device)
			
		
	
	def row_setup_event(self, iter, device):
		props = device.GetProperties()


		try:
			klass = get_minor_class(props["Class"])
		except:
			klass = "Unknown"
		
		icon = self.get_device_icon(klass)
		
		#cicon = make_device_icon(icon, "Paired" in props and props["Paired"], "Trusted" in props and props["Trusted"], fake) 
		

		name = props["Alias"]
		address = props["Address"]

		caption = "<span size='x-large'>%(0)s</span>\n<span size='small'>%(1)s</span>\n<i>%(2)s</i>" % {"0":name, "1":klass.capitalize(), "2":address}
		self.set(iter, caption=caption, orig_icon=icon)
		
		self.row_update_event(iter, "Fake", device.Fake)
		
		try:
			self.row_update_event(iter, "Trusted", props["Trusted"])
		except:
			pass
		try:
			self.row_update_event(iter, "Paired", props["Paired"])
		except:
			pass

	def row_update_event(self, iter, key, value):

		if key == "Trusted":
			row = self.get(iter, "bonded", "orig_icon")
			if value:
				icon = make_device_icon(row["orig_icon"], row["bonded"], True, False) 
				self.set(iter, device_pb=icon, trusted=True)
			else:
				icon = make_device_icon(row["orig_icon"], row["bonded"], False, False) 
				self.set(iter, device_pb=icon, trusted=False)
			
		
		elif key == "Paired":
			row = self.get(iter, "trusted", "orig_icon")
			if value:
				icon = make_device_icon(row["orig_icon"], True, row["trusted"], False) 
				self.set(iter, device_pb=icon, bonded=True)
			else:
				icon = make_device_icon(row["orig_icon"], False, row["trusted"], False) 
				self.set(iter, device_pb=icon, bonded=False)
				
		elif key == "Fake":
			row = self.get(iter, "bonded", "trusted", "orig_icon")
			if value:
				icon = make_device_icon(row["orig_icon"], False, False, True) 
				self.set(iter, device_pb=icon, fake=True)
			else:
				icon = make_device_icon(row["orig_icon"], row["bonded"], row["trusted"], False) 
				self.set(iter, device_pb=icon, fake=False)
				
				
	
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
						tpl_pb=get_icon("blueman-tpl-%s" % rnd(tpl_perc), 48),
						rssi=rssi_perc,
						lq=lq_perc,
						tpl=tpl_perc,
						connected=True)
			else:
				self.set(iter, rssi_pb=None, lq_pb=None, tpl_pb=None, connected=False)
		else:
			print "invisible"
		#set_signal("rssi", rssi_perc, "/signal/rssi/rssi_", ".png", self.row)
		#set_signal("lq", lq_perc, "/signal/lq/lq_", ".png", self.row)
		#set_signal("tpl", tpl_perc, "/signal/tpl/tpl_", ".png", self.row)
		
	
	def tooltip_query(self, tw, x, y, kb, tooltip):

		#print args
		#args[4].set_text("test"+str(args[1]))

		path = self.get_path_at_pos(x, y)


		if path:
			if path[0][0] != self.tooltip_row or path[1] != self.tooltip_col:
				self.tooltip_row = path[0][0]
				self.tooltip_col = path[1]
				return False
			
			if path[1] == self.columns["device_pb"]:
				iter = self.get_iter(path[0][0])
				
				row = self.get(iter, "trusted", "bonded")
				trusted = row["trusted"]
				bonded = row["bonded"]
				if trusted and bonded:
					tooltip.set_markup(_("<b>Trusted and Bonded</b>"))
				elif bonded:
					tooltip.set_markup(_("<b>Bonded</b>"))
				elif trusted:
					tooltip.set_markup(_("<b>Trusted</b>"))
				else:
					return False
				
					
				self.tooltip_row = path[0][0]
				self.tooltip_col = path[1]
				return True

			
			if path[1] == self.columns["tpl_pb"] or path[1] == self.columns["lq_pb"] or path[1] == self.columns["rssi_pb"]:
				iter = self.get_iter(path[0][0])

				dt = self.get(iter, "connected")["connected"]
				#print dt
				if dt:
					rssi = self.get(iter, "rssi")["rssi"]
					lq = self.get(iter, "lq")["lq"]
					tpl = self.get(iter, "tpl")["tpl"]
					
					if rssi < 30:
						rssi_state = _("Poor")
					
					if rssi < 40 and rssi > 30:
						rssi_state = _("Sub-optimal")

					elif rssi > 40 and rssi < 60:
						rssi_state = _("Optimal")
					
					elif rssi > 60:
						rssi_state = _("Much")
					
					elif rssi > 70:
						rssi_state = _("Too much")
						
					
					if tpl < 30:
						tpl_state = _("Low")
					
					if tpl < 40 and tpl > 30:
						tpl_state = _("Sub-optimal")

					elif tpl > 40 and rssi < 60:
						tpl_state = _("Optimal")
					
					elif tpl > 60:
						tpl_state = _("High")
					
					elif tpl > 70:
						tpl_state = _("Very High")
						
											
					tooltip.set_markup(_("<b>Connected</b>\nReceived Signal Strength: %(rssi)u%% <i>(%(rssi_state)s)</i>\nLink Quality: %(lq)u%%\nTransmit Power Level: %(tpl)u%% <i>(%(tpl_state)s)</i>") % {"rssi_state": rssi_state, "rssi":rssi, "lq":lq, "tpl":tpl, "tpl_state": tpl_state})
					self.tooltip_row = path[0][0]
					self.tooltip_col = path[1]
					return True	
		return False
			

