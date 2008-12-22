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
import os
import gtk
import dbus
import gettext
import time
import atexit
import marshal
import base64
import gtk.gdk
import zlib
from blueman.main.Config import Config
from blueman.Functions import *
from blueman.main.Device import Device
import blueman.Sdp as sdp


_ = gettext.gettext


def store_state():
	for i in RecentConns.items:
		i["device"] = None
		i["mitem"] = None
		i["gsignal"] = 0
		
	dump = base64.b64encode(zlib.compress(marshal.dumps(RecentConns.items), 9))
	
	c = Config()
	c.props.recent_connections = dump

atexit.register(store_state)

class RecentConns(gtk.Menu):
	
	items = None
	
	def __init__(self, applet):
		self.Item = applet.recent_item
		self.Applet = applet
		gtk.Menu.__init__(self)
		
		
	def initialize(self):
		def compare_by (fieldname):
			def compare_two_dicts (a, b):
				return cmp(a[fieldname], b[fieldname])
			return compare_two_dicts
		
		def each(child):
			self.remove(child)
		self.foreach(each)

		RecentConns.items.sort(compare_by("time"))
		RecentConns.items = RecentConns.items[0:5]
		
		if len(RecentConns.items) == 0:
			self.Item.props.sensitive = False
		else:
			self.Item.props.sensitive = True

		count = 0
		for item in RecentConns.items:
			if count < 5:
				self.add_item(item)
				count+=1
	#set bluez manager interface
	def set_manager(self, manager):
		self.Manager = manager
		if RecentConns.items != None:
			for i in reversed(RecentConns.items):
				try:
					if i["device"]:
						if i["gsignal"]:
							i["device"].disconnect(i["gsignal"])
						i["device"].Destroy()
					i["device"] = self.get_device(i)
					i["gsignal"] = i["device"].connect("invalidated", self.on_device_removed, i)
				except:
					RecentConns.items.remove(i)
		else:
			self.recover_state()
		
		self.initialize()
	
	def on_device_removed(self, device, item):
		device.disconnect(item["gsignal"])
		RecentConns.items.remove(item)
		self.initialize()
		
	def notify(self, device, service_interface, conn_args):
		item = {}
		object_path = device.GetObjectPath()
		item["adapter"] = os.path.basename(object_path.replace("/"+os.path.basename(object_path), ""))
		item["address"] = device.Address
		item["service"] = service_interface
		item["conn_args"] = conn_args
		item["time"] = time.time()
		item["device"] = device #device object
		item["mitem"] = None #menu item object
		item["gsignal"] = item["device"].connect("invalidated", self.on_device_removed, item)
		
		for i in RecentConns.items:
			if i["adapter"] == item["adapter"] and \
			   i["address"] == item["address"] and \
			   i["service"] == item["service"] and \
			   i["conn_args"] == item["conn_args"]:
				i["time"] = item["time"]
				i["device"] = item["device"]
				self.initialize()
				return
		
		RecentConns.items.append(item)
		self.initialize()
		
	def on_item_activated(self, menu_item, item):
		print "Connect", item["address"], item["service"]
		
		sv_name = item["service"].split(".")[-1].lower()
		try:
			service = item["device"].Services[sv_name]
		except:
			RecentConns.items.remove(item)
		else:
			c = gtk.gdk.Cursor(gtk.gdk.WATCH)
			cn = gtk.gdk.Cursor(gtk.gdk.ARROW)
			screen = gtk.gdk.screen_get_default()
			
			
			def reply(*args):
				self.Applet.show_notification(_("Connected"), _("Connected to %s") % item["mitem"].get_child().props.label, pixbuf=get_icon("gtk-connect", 48))
				item["mitem"].props.sensitive = True
				screen.get_root_window().set_cursor(cn)
				
			def err(reason):
				self.Applet.show_notification(_("Failed to connect"), str(reason).split(": ")[-1], pixbuf=get_icon("gtk-dialog-error", 48))
				item["mitem"].props.sensitive = True
				screen.get_root_window().set_cursor(cn)
			

			screen.get_root_window().set_cursor(c)
			
			service.Connect(reply_handler=reply, error_handler=err, *item["conn_args"])
			
			item["time"] = time.time()
			self.initialize()
			item["mitem"].props.sensitive = False
			
		
	def add_item(self, item):
		device = item["device"]
		
		if item["service"] == "org.bluez.Serial":
			name = sdp.uuid16_to_name(sdp.uuid128_to_uuid16(item["conn_args"][0]))
		elif item["service"] == "org.bluez.Network":
			name = _("Network Access (%s)") % sdp.uuid16_to_name(sdp.uuid128_to_uuid16(item["conn_args"][0]))
		else:
			name = item["service"].split(".")[-1] + " " + _("Service")
			name = name.capitalize()
		
		

		mitem = create_menuitem(_("%(service)s on %(device)s") % {"service":name, "device":device.Alias}, get_icon(device.Icon, 16))
		item["mitem"] = mitem
		mitem.connect("activate", self.on_item_activated, item)

		
		self.prepend(mitem)
		mitem.show()
		
		
		
	def get_device(self, item):
		adapter = self.Manager.GetAdapter(item["adapter"])
		return Device(adapter.FindDevice(item["address"]))
		
		
	def recover_state(self):
		c = Config()
		dump = c.props.recent_connections
		try:
			items = marshal.loads(zlib.decompress(base64.b64decode(dump)))
		except:
			items = None
		if items == None:
			RecentConns.items = []
			return
		
		for i in reversed(items):
			#try:
			i["device"] = self.get_device(i)
			i["gsignal"] = i["device"].connect("invalidated", self.on_device_removed, i)
			#except Exe:
			#	items.remove(i)
			
		RecentConns.items = items
		
