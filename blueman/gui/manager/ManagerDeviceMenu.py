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
from blueman.main.Config import Config
from blueman.main.AppletService import AppletService

from blueman.Lib import rfcomm_list

import gettext
_ = gettext.gettext

class ManagerDeviceMenu(gtk.Menu):

	__ops__ = {}
	__instances__ = []
	
	def __init__(self, blueman):
		gtk.Menu.__init__(self)
		self.Blueman = blueman
		self.SelectedDevice = None

		self.is_popup = False
		
		#object, args,
		self.Signals = SignalTracker()
		self.MainSignals = SignalTracker()
		
		self.MainSignals.Handle("gobject", self.Blueman.List, "device-property-changed", self.on_device_property_changed)

		ManagerDeviceMenu.__instances__.append(self)
		
		self.Generate()

		

	def __del__(self):
		dprint("deleting devicemenu")
	#	gobject.GObject.__del__(self)
	
	
	def popup(self, *args):
		self.is_popup = True
		
		self.MainSignals.DisconnectAll()
		self.MainSignals.Handle("gobject", self.Blueman.List, "device-property-changed", self.on_device_property_changed)

		def disconnectall(x):
			self.MainSignals.DisconnectAll()
		
		self.MainSignals.Handle("gobject", self, "selection-done", disconnectall)

		self.Generate()
		
		gtk.Menu.popup(self, *args)
	
	def clear(self):
		self.Signals.DisconnectAll()
		def each(child):
			self.remove(child)
			
		self.foreach(each)
	
	def set_op(self, device, message):
		ManagerDeviceMenu.__ops__[device.GetObjectPath()] = message
		for inst in ManagerDeviceMenu.__instances__:
			dprint("op: regenerating instance", inst)
			if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
				inst.Generate()

	
	def get_op(self, device):
		try:
			return ManagerDeviceMenu.__ops__[device.GetObjectPath()]
		except:
			return None
		
	def unset_op(self, device):
		del ManagerDeviceMenu.__ops__[device.GetObjectPath()]
		for inst in ManagerDeviceMenu.__instances__:
			dprint("op: regenerating instance", inst)
			if inst.SelectedDevice == self.SelectedDevice and not (inst.is_popup and not inst.props.visible):
				inst.Generate()

		
	def service_property_changed(self, key, value):
		if key == "Connected":
			self.Generate()
		

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
			
			dprint("success", args2)
			prog_msg(_("Success!"))
			self.unset_op(device)

			
		def fail(*args):
			
			prog_msg(_("Failed"))
			
			self.unset_op(device)
			dprint("fail", args)

			
		def cancel(prog, *args):
			try:
				svc.Disconnect(*args)
			except:
				pass
			prog_msg(_("Cancelled"))
			self.unset_op(device)
		
		svc = device.Services[service_id]
		self.set_op(device, _("Connecting..."))
		prog = ManagerProgressbar(self.Blueman, False)
		
		try:
			appl = AppletService()
		except:
			dprint("** Failed to connect to applet")
			fail()
			return
		
		if service_id == "network":
			uuid = args[0]
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Connect", [uuid], reply_handler=success, error_handler=fail)
			#prog.set_cancellable(True)
			#prog.connect("cancelled", cancel)
			
		elif service_id == "input":
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Connect", [], reply_handler=success, error_handler=fail)
			#prog.connect("cancelled", cancel)
			
		elif service_id == "serial":
			uuid = args[0]

			appl.RfcommConnect(device.GetObjectPath(), uuid, reply_handler=success, error_handler=fail)
		
		else:
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Connect", [], reply_handler=success, error_handler=fail)
			
			
			
		prog.start()
		
	def on_disconnect(self, item, device, service_id, *args):
		svc = device.Services[service_id]
		if service_id == "serial":
			try:
				appl = AppletService()
			except:
				dprint("** Failed to connect to applet")
			else:
				appl.RfcommDisconnect(device.GetObjectPath(), args[0])
				self.Generate()
		else:
			try:
				appl = AppletService()
			except:
				dprint("** Failed to connect to applet")
				return
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Disconnect", [])
		
		
		
	def on_device_property_changed(self, List, device, iter, (key, value)):
#		print "menu:", key, value
		if List.compare(iter, List.selected()):
			if key == "Connected"\
			or key =="Fake"\
			or key == "UUIDs"\
			or key == "Trusted"\
			or key == "Paired":
				self.Generate()

		
	def Generate(self):
		dprint("Gen")

		self.clear()
		
		if not self.is_popup or self.props.visible:
			device = self.Blueman.List.get(self.Blueman.List.selected(), "device")["device"]
		else:
			(x,y) = self.Blueman.List.get_pointer()
			path = self.Blueman.List.get_path_at_pos(x, y)
			if path != None:
				device = self.Blueman.List.get(path[0][0], "device")["device"]
			else:
				return
				
		if not device.Valid:
			return
		self.SelectedDevice = device
		
		op = self.get_op(device)
		
		if op != None:
			item = create_menuitem(op, get_icon("gtk-connect", 16))
			item.props.sensitive = False
			item.show()
			self.append(item)
			return
		
		
		if device.Fake:
			item = create_menuitem(_("Add Device"), get_icon("gtk-add", 16))
			self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.add_device(device))
			item.show()
			self.append(item)
			item.props.tooltip_text = _("Add this device to known devices list")
			
			item = create_menuitem(_("Setup..."), get_icon("gtk-properties", 16))
			self.append(item)
			self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.setup(device))
			item.show()
			item.props.tooltip_text = _("Run the setup assistant for this device")
			
			item = create_menuitem(_("Bond"), get_icon("gtk-dialog-authentication", 16))
			self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.bond(device))
			self.append(item)
			item.show()			
			item.props.tooltip_text = _("Create bonding with the device")
			
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			send_item = create_menuitem(_("Send a file..."), get_icon("gtk-copy", 16))
			self.Signals.Handle("gobject", send_item, "activate", lambda x: self.Blueman.send(device))
			send_item.show()
			self.append(send_item)
			
			
			
		else:
			
			
			uuids = device.UUIDs
			item = None
			for name, service in device.Services.iteritems():
				if name == "serial":
					
					
					sub = gtk.Menu()
					sub.show()

					num_ports = 0
					for uuid in uuids:
						
						uuid16 = uuid128_to_uuid16(uuid)
						if uuid16 == DIALUP_NET_SVCLASS_ID:
							item = create_menuitem(_("Dialup Service"), get_icon("modem", 16))
							self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
							sub.append(item)
							item.show()
							num_ports += 1
							
						if uuid16 == SERIAL_PORT_SVCLASS_ID:
							item = create_menuitem(_("Serial Service"), get_icon("modem", 16))
							self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
							sub.append(item)
							item.show()
							num_ports += 1
							
					if num_ports > 0:
#						def on_type_changed(item, type):
#							if item.active:
#								setattr(conns.props, device.Address, type)
#							
#						conns = Config("conn_types")
						
						item = create_menuitem(_("Serial Ports"), get_icon("modem", 16))
						item.set_submenu(sub)
						item.show()
						self.append(item)
						
#						item = gtk.SeparatorMenuItem()
#						item.show()
#						sub.append(item)
#						
#						gsm_item = gtk.RadioMenuItem(None, "GSM/3G")
#						gsm_item.show()
#						
#						sub.append(gsm_item)
#						
#						cdma_item = gtk.RadioMenuItem(gsm_item, "CDMA")
#						cdma_item.show()
#						
#						sub.append(cdma_item)		
#						
#						t = getattr(conns.props, device.Address)
#						if t == None or t == 0:
#							gsm_item.set_active(True)
#						else:
#							cdma_item.set_active(True)
#						
#						gsm_item.connect("activate", on_type_changed, 0)	
#						cdma_item.connect("activate", on_type_changed, 1)		
					
					rfcomms = rfcomm_list()
					
					sep = False
					for dev in rfcomms:
						if dev["dst"] == device.Address:
							if dev["state"] == "connected":
								if not sep:
									item = gtk.SeparatorMenuItem()
									item.show()
									sub.append(item)
									sep = True
								
								devname = "/dev/rfcomm%s" % dev["id"]
							
								item = create_menuitem(_("Disconnect %s") % "rfcomm%d" % dev["id"], get_icon("gtk-disconnect", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name, devname)
								sub.append(item)
								item.show()
					
							
					
				if name == "input":
					self.Signals.Handle("bluez", service, self.service_property_changed, "PropertyChanged")
					sprops = service.GetProperties()
					if sprops["Connected"]:
						item = create_menuitem(_("Disconnect Input Service"), get_icon("mouse", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)

					else:
						item = create_menuitem(_("Connect Input Service"), get_icon("mouse", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)

					item.show()
					self.append(item)
					
				if name == "network":
					self.Signals.Handle("bluez", service, self.service_property_changed, "PropertyChanged")
					sprops = service.GetProperties()
					
					if not sprops["Connected"]:
						item = create_menuitem(_("Network Access"), get_icon("network", 16))
						item.show()
						self.append(item)
						sub = gtk.Menu()
						sub.show()
						item.set_submenu(sub)
						
						added = False
						for uuid in uuids:

							uuid16 = uuid128_to_uuid16(uuid)
							if uuid16 == GN_SVCLASS_ID:
								item = create_menuitem(_("Group Network"), get_icon("network-server", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
								sub.append(item)
								item.show()
								added = True
							
							if uuid16 == NAP_SVCLASS_ID:
								item = create_menuitem(_("Network Access Point"), get_icon("network-server", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
								sub.append(item)
								item.show()
								added = True
						if not added:
							item.destroy()
							item = None
					else:
						item = create_menuitem(_("Disconnect Network"), get_icon("gtk-disconnect", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
						item.show()
						self.append(item)
						
						c = Config("network")
						if c.props.dhcp_client:
							def renew(x):
								try:
									appl = AppletService()
								except:
									dprint("** Failed to connect to applet")
								else:
							
									appl.DhcpClient(sprops["Device"])
					
							item = create_menuitem(_("Renew IP Address"), get_icon("gtk-refresh", 16))
							self.Signals.Handle("gobject", item, "activate", renew)
							item.show()
							self.append(item)

					
				if name == "headset":
					sprops = service.GetProperties()
					
					if sprops["Connected"]:
						item = create_menuitem(_("Disconnect Headset Service"), get_icon("blueman-handsfree", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
					else:
						item = create_menuitem(_("Connect Headset Service"), get_icon("blueman-handsfree", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)
					item.show()
					self.append(item)
					

				if name == "audiosink":
					sprops = service.GetProperties()
					
					if sprops["Connected"]:
						item = create_menuitem(_("Disconnect A2DP Service"), get_icon("blueman-headset", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
					else:
						item = create_menuitem(_("Connect A2DP Service"), get_icon("blueman-headset", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)
					item.show()
					self.append(item)
					
			if item:
				item = gtk.SeparatorMenuItem()
				item.show()
				self.append(item)

			send_item = create_menuitem(_("Send a file..."), get_icon("gtk-copy", 16))
			send_item.props.sensitive = False
			self.append(send_item)
			send_item.show()
			
			browse_item = create_menuitem(_("Browse device..."), get_icon("gtk-open", 16))
			browse_item.props.sensitive = False
			self.append(browse_item)
			browse_item.show()			

			for uuid in uuids:
				uuid16 = uuid128_to_uuid16(uuid)
				if uuid16 == OBEX_OBJPUSH_SVCLASS_ID:
					self.Signals.Handle("gobject", send_item, "activate", lambda x: self.Blueman.send(device))
					send_item.props.sensitive = True

					
				if uuid16 == OBEX_FILETRANS_SVCLASS_ID:
					self.Signals.Handle("gobject", browse_item, "activate", lambda x: self.Blueman.browse(device))
					browse_item.props.sensitive = True

					

			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			item = create_menuitem(_("Bond"), get_icon("gtk-dialog-authentication", 16))
			item.props.tooltip_text = _("Create bonding with the device")
			self.append(item)
			item.show()
			if not device.Paired:
				self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.bond(device))
			else:
				item.props.sensitive = False

				
			if not device.Trusted:
				item = create_menuitem(_("Trust"), get_icon("blueman-trust", 16))
				self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.toggle_trust(device))
				self.append(item)
				item.show()
			else:
				item = create_menuitem(_("Untrust"), get_icon("blueman-untrust", 16))
				self.append(item)
				self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.toggle_trust(device))
				item.show()
			item.props.tooltip_text = _("Mark/Unmark this device as trusted")
				
			item = create_menuitem(_("Setup..."), get_icon("gtk-properties", 16))
			self.append(item)
			self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.setup(device))
			item.show()
			item.props.tooltip_text = _("Run the setup assistant for this device")
			
			def update_services(item):
				def prog_msg(msg):
					prog.stop()
					prog.set_label(msg)
					prog.set_cancellable(False)
					self.unset_op(device)
					gobject.timeout_add(1500, prog.finalize)
				
				def reply(*args):
					prog_msg(_("Success!"))
					
				def error(*args):
					dprint("err", args)
					prog_msg(_("Fail"))
				prog = ManagerProgressbar(self.Blueman, False, _("Refreshing"))
				prog.start()
				self.set_op(device, _("Refreshing Services..."))
				device.GetInterface().DiscoverServices("", reply_handler=reply, error_handler=error)
			
			item = create_menuitem(_("Refresh Services"), get_icon("gtk-refresh", 16))
			self.append(item)
			self.Signals.Handle(item, "activate", update_services)
			item.show()
			
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			item = create_menuitem(_("Remove..."), get_icon("gtk-delete", 16))
			self.Signals.Handle(item, "activate", lambda x: self.Blueman.remove(device))
			self.append(item)
			item.show()
			item.props.tooltip_text = _("Remove this device from the known devices list")
			
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			item = create_menuitem(_("Disconnect Device"), get_icon("gtk-disconnect", 16))
			self.append(item)
			item.show()
			if device.Connected:
				self.Signals.Handle(item, "activate", lambda x: self.Blueman.disconnect(device))

			else:
				item.props.sensitive = False
				


		
