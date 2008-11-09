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

import gobject
import gtk
from blueman.Sdp import *
from blueman.Functions import *
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar

from blueman.main.manager.Applet import Applet

from blueman.Lib import rfcomm_list

import gettext
_ = gettext.gettext

class ManagerDeviceMenu(gtk.Menu):

	__ops__ = {}
	
	def __init__(self, blueman):
		gtk.Menu.__init__(self)
		self.Blueman = blueman

		
		
		#object, args,
		self.Signals = SignalTracker()
		
		self.Blueman.List.connect("device-property-changed", self.on_device_property_changed)
		self.Generate()

		

	def __del__(self):
		print "deleting devicemenu"
	#	gobject.GObject.__del__(self)
	
	
	def clear(self):
		self.Signals.DisconnectAll()
		def each(child):
			self.remove(child)
			
		self.foreach(each)
	
	def set_op(self, device, message):
		ManagerDeviceMenu.__ops__[device.GetObjectPath()] = message
		
	def get_op(self, device):
		try:
			return ManagerDeviceMenu.__ops__[device.GetObjectPath()]
		except:
			return None
		
	def unset_op(self, device):
		del ManagerDeviceMenu.__ops__[device.GetObjectPath()]
	
		
	def service_property_changed(self, key, value):
		if key == "Connected":
			self.Generate()
		
		
		
	def create_menuitem(self, text, image):
		item = gtk.ImageMenuItem()
		item.set_image(gtk.image_new_from_pixbuf(image))
		
		label = gtk.Label()
		label.set_text(text)
		label.set_alignment(0,0.5)

		label.show()
		
		item.add(label)
		
		return item
		
		
	def on_connect(self, item, device, service_id, *args):
		def prog_msg(msg):
			prog.stop()
			prog.set_label(msg)
			prog.set_cancellable(False)
			gobject.timeout_add(1500, prog.finalize)
		
		def success(*args2):
			#uuid16 = uuid128_to_uuid16(args[0])
			#if service_id == "serial": #and uuid16 == DIALUP_NET_SVCLASS_ID:
			#	dev = args[0]
			#	appl.register_modem(device.GetObjectPath(), dev)
			
			print "success", args2
			prog_msg(_("Success!"))
			self.unset_op(device)
			self.Generate()
			
		def fail(*args):
			
			prog_msg(_("Failed"))
			
			self.unset_op(device)
			print "fail", args
			self.Generate()
			
		def cancel(prog, *args):
			try:
				svc.Disconnect(*args)
			except:
				pass
			prog_msg("Cancelled")
			self.unset_op(device)
		
		svc = device.Services[service_id]
		self.set_op(device, "Connecting...")
		prog = ManagerProgressbar(self.Blueman, False)
		
		if service_id == "network":
			uuid = args[0]
			svc.Connect(uuid, reply_handler=success, error_handler=fail)
			#prog.set_cancellable(True)
			#prog.connect("cancelled", cancel)
			
		elif service_id == "input":
			svc.Connect(reply_handler=success, error_handler=fail)
			#prog.connect("cancelled", cancel)
			
		elif service_id == "serial":
			uuid = args[0]
			appl = Applet()
			appl.rfcomm_connect(device.GetObjectPath(), uuid, reply_handler=success, error_handler=fail)
		
		else:
			svc.Connect(reply_handler=success, error_handler=fail)
			
			
			
		prog.start()
		self.Generate()
		
	def on_disconnect(self, item, device, service_id, *args):
		svc = device.Services[service_id]
		if service_id == "serial":
			a = Applet()
			a.rfcomm_disconnect(device.GetObjectPath(), args[0])
			self.Generate()
		else:
			svc.Disconnect()
		
		
		
	def on_device_property_changed(self, List, device, iter, (key, value)):
		if List.compare(iter, List.selected()):
			if key == "Connected":
				self.Generate()
			if key == "Fake":
				self.Generate()
		
	def Generate(self):
		print "Gen"
		self.clear()
		
		device = self.Blueman.List.get(self.Blueman.List.selected(), "device")["device"]
		
		
		op = self.get_op(device)
		
		if op != None:
			item = self.create_menuitem(op, get_icon("gtk-connect", 16))
			item.props.sensitive = False
			item.show()
			self.append(item)
			return
		
		
		props = device.GetProperties()
		
		if "Fake" in props:
			print "fake device"
			
			
		else:
			
			
			uuids = props["UUIDs"]
			
			
			for name, service in device.Services.iteritems():
				if name == "serial":
					
					item = self.create_menuitem(_("Serial Ports"), get_icon("modem", 16))
					sub = gtk.Menu()
					sub.show()
					item.set_submenu(sub)
					item.show()
					self.append(item)
					for uuid in uuids:
						
						uuid16 = uuid128_to_uuid16(uuid)
						if uuid16 == DIALUP_NET_SVCLASS_ID:
							item = self.create_menuitem(_("Dialup Service"), get_icon("modem", 16))
							item.connect("activate", self.on_connect, device, name, uuid)
							sub.append(item)
							item.show()
							
						if uuid16 == SERIAL_PORT_SVCLASS_ID:
							item = self.create_menuitem(_("Serial Service"), get_icon("modem", 16))
							item.connect("activate", self.on_connect, device, name, uuid)
							sub.append(item)
							item.show()
							
					item = gtk.SeparatorMenuItem()
					item.show()
					sub.append(item)
							
					rfcomms = rfcomm_list()
					for dev in rfcomms:
						if dev["dst"] == props["Address"]:
							if dev["state"] == "connected":
								devname = "/dev/rfcomm%s" % dev["id"]
							
								item = self.create_menuitem(_("Disconnect %s" % devname), get_icon("gtk-disconnect", 16))
								item.connect("activate", self.on_disconnect, device, name, devname)
								sub.append(item)
								item.show()
					
							
					
				if name == "input":
					self.Signals.Handle(service, self.service_property_changed, "PropertyChanged")
					sprops = service.GetProperties()
					if sprops["Connected"]:
						item = self.create_menuitem(_("Disconnect Input Service"), get_icon("mouse", 16))
						item.connect("activate", self.on_disconnect, device, name)
					else:
						item = self.create_menuitem(_("Connect Input Service"), get_icon("mouse", 16))
						item.connect("activate", self.on_connect, device, name)
					item.show()
					self.append(item)
					
				if name == "network":
					self.Signals.Handle(service, self.service_property_changed, "PropertyChanged")
					sprops = service.GetProperties()
					
					if not sprops["Connected"]:
						item = self.create_menuitem(_("Network Access"), get_icon("network", 16))
						item.show()
						self.append(item)
						sub = gtk.Menu()
						sub.show()
						item.set_submenu(sub)
					
						for uuid in uuids:

							uuid16 = uuid128_to_uuid16(uuid)
							if uuid16 == GN_SVCLASS_ID:
								item = self.create_menuitem(_("Group Network"), get_icon("network-server", 16))
								item.connect("activate", self.on_connect, device, name, uuid)
								sub.append(item)
								item.show()
							
							if uuid16 == NAP_SVCLASS_ID:
								item = self.create_menuitem(_("Network Access Point"), get_icon("network-server", 16))
								item.connect("activate", self.on_connect, device, name, uuid)
								sub.append(item)
								item.show()
					else:
						item = self.create_menuitem(_("Disconnect Network"), get_icon("gtk-disconnect", 16))
						item.connect("activate", self.on_disconnect, device, name)
						item.show()
						self.append(item)
					
					

					
				if name == "headset":
					sprops = service.GetProperties()
					
					if sprops["Connected"]:
						item = self.create_menuitem(_("Disconnect Headset Service"), get_icon("audio", 16))
						item.connect("activate", self.on_connect, device, name)
					else:
						item = self.create_menuitem(_("Connect Headset Service"), get_icon("audio", 16))
						item.connect("activate", self.on_disconnect, device, name)
					item.show()
					self.append(item)
					

				if name == "audiosink":
					sprops = service.GetProperties()
					
					if sprops["Connected"]:
						item = self.create_menuitem(_("Disconnect A2DP Service"), get_icon("audio", 16))
						item.connect("activate", self.on_connect, device, name)
					else:
						item = self.create_menuitem(_("Connect A2DP Service"), get_icon("audio", 16))
						item.connect("activate", self.on_disconnect, device, name)
					item.show()
					self.append(item)
					
					
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)

			send_item = self.create_menuitem(_("Send a file..."), get_icon("gtk-copy", 16))
			send_item.props.sensitive = False
			self.append(send_item)
			send_item.show()
			
			browse_item = self.create_menuitem(_("Browse device..."), get_icon("gtk-open", 16))
			browse_item.props.sensitive = False
			self.append(browse_item)
			browse_item.show()			

			for uuid in uuids:
				uuid16 = uuid128_to_uuid16(uuid)
				if uuid16 == OBEX_OBJPUSH_SVCLASS_ID:
					#connect
					send_item.props.sensitive = True

					
				if uuid16 == OBEX_FILETRANS_SVCLASS_ID:
					#connect
					browse_item.props.sensitive = True

					

			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			item = self.create_menuitem(_("Bond"), get_icon("gtk-dialog-authentication", 16))
			self.append(item)
			item.show()
			if not props["Paired"]:
				#connect
				pass
			else:
				item.props.sensitive = False

				
			if not props["Trusted"]:
				item = self.create_menuitem(_("Trust"), get_icon("blueman-trust", 16))
				self.append(item)
				item.show()
			else:
				item = self.create_menuitem(_("Untrust"), get_icon("blueman-untrust", 16))
				self.append(item)
				item.show()
				
			item = self.create_menuitem(_("Setup..."), get_icon("gtk-properties", 16))
			self.append(item)
			item.show()
			
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			item = self.create_menuitem(_("Remove..."), get_icon("gtk-delete", 16))
			self.append(item)
			item.show()
			
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			item = self.create_menuitem(_("Disconnect Device"), get_icon("gtk-disconnect", 16))
			self.append(item)
			item.show()
			if props["Connected"]:
				#connect
				pass
			else:
				item.props.sensitive = False
				


		
