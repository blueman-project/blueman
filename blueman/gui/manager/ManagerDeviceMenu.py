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
from blueman.gui.MessageArea import MessageArea

from blueman.Lib import rfcomm_list

def get_x_icon(icon_name, size):
	ic = get_icon(icon_name, size) 
	x = get_icon("blueman-x", 8) 
	pixbuf = composite_icon(ic, [(x, ic.props.height - 8, ic.props.height - 8, 200)])
	
	return pixbuf

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
			try:
				uuid16 = uuid128_to_uuid16(args[0])
			except:
				uuid16 = 0
			
			dprint("success", args2)
			prog_msg(_("Success!"))
			
			
			if service_id == "serial" and uuid16 == SERIAL_PORT_SVCLASS_ID:
				MessageArea.show_message(_("Serial port connected to %s") % args2[0], gtk.STOCK_DIALOG_INFO)
			else:
				MessageArea.close()
			
			self.unset_op(device)
			
		def fail(*args):
			prog_msg(_("Failed"))
			
			self.unset_op(device)
			dprint("fail", args)
			MessageArea.show_message(_("Connection Failed: ") + e_(str(args[0])))
			
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
		try:
			appl.SetTimeHint(gtk.get_current_event_time())
		except:
			pass
			
		if service_id == "network":
			uuid = args[0]
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Connect", [uuid], reply_handler=success, error_handler=fail, timeout=200)
			#prog.set_cancellable(True)
			#prog.connect("cancelled", cancel)
			
		elif service_id == "input":
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Connect", [], reply_handler=success, error_handler=fail, timeout=200)
			#prog.connect("cancelled", cancel)
			
		elif service_id == "serial":
			uuid = str(args[0])

			appl.RfcommConnect(device.GetObjectPath(), uuid, reply_handler=success, error_handler=fail, timeout=200)
		
		else:
			appl.ServiceProxy(svc.GetInterfaceName(), svc.GetObjectPath(), "Connect", [], reply_handler=success, error_handler=fail, timeout=200)
			
			
			
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
		self.clear()
		
		appl = AppletService()	
		
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
			
			item = create_menuitem(_("Pair"), get_icon("gtk-dialog-authentication", 16))
			self.Signals.Handle("gobject", item, "activate", lambda x: self.Blueman.bond(device))
			self.append(item)
			item.show()			
			item.props.tooltip_text = _("Create pairing with the device")
			
			item = gtk.SeparatorMenuItem()
			item.show()
			self.append(item)
			
			send_item = create_menuitem(_("Send a file..."), get_icon("gtk-copy", 16))
			self.Signals.Handle("gobject", send_item, "activate", lambda x: self.Blueman.send(device))
			send_item.show()
			self.append(send_item)
			
			
			
		else:
			dprint(device.Alias)
			uuids = device.UUIDs
			item = None
			items = []
			for name, service in device.Services.iteritems():
				if name == "serial":
					ports_list = rfcomm_list()
					def flt(dev):
						if dev["dst"] == device.Address and dev["state"] == "connected":
							return dev["channel"]
					
					active_ports = map(flt, ports_list)
					
					
					def get_port_id(channel):
						for dev in ports_list:
							if dev["dst"] == device.Address and dev["state"] == "connected" and dev["channel"] == channel:
								return dev["id"]
					
					serial_items = []

					num_ports = 0
					has_dun = False		
					try:
						for port_name, channel, uuid in sdp_get_cached_rfcomm(device.Address):
							
							if SERIAL_PORT_SVCLASS_ID in uuid:
								if name is not None:
									if channel in active_ports:
										item = create_menuitem(port_name, get_x_icon("blueman-serial", 16))
										self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name, "/dev/rfcomm%d" % get_port_id(channel))
										item.show()
										items.append((150, item))
									else:
										item = create_menuitem(port_name, get_icon("blueman-serial", 16))
										self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, channel)
										item.show()
										serial_items.append(item)

								
							elif DIALUP_NET_SVCLASS_ID in uuid:
								if name is not None:
									if channel in active_ports:
										item = create_menuitem(port_name, get_x_icon("modem", 16))
										self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name, "/dev/rfcomm%d" % get_port_id(channel))
										item.show()
										items.append((150, item))
									else:
										item = create_menuitem(port_name, get_icon("modem", 16))
										self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, channel)
										item.show()
										serial_items.append(item)
										has_dun = True
							
					except KeyError:
						for uuid in uuids:
							uuid16 = uuid128_to_uuid16(uuid)
							if uuid16 == DIALUP_NET_SVCLASS_ID:
								item = create_menuitem(_("Dialup Service"), get_icon("modem", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
								item.show()
								serial_items.append(item)
								has_dun = True
								
							if uuid16 == SERIAL_PORT_SVCLASS_ID:
								item = create_menuitem(_("Serial Service"), get_icon("blueman-serial", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
								item.show()
								serial_items.append(item)
								
								
						for dev in ports_list:
							if dev["dst"] == device.Address:
								if dev["state"] == "connected":
									devname = _("Serial Port %s") % "rfcomm%d" % dev["id"]
						
									item = create_menuitem(devname, get_x_icon("modem", 16))
									self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name, "/dev/rfcomm%d" % dev["id"])
									items.append((120, item))
									item.show()
				
					def open_settings(i, device):
						from blueman.gui.GsmSettings import GsmSettings
						d = GsmSettings(device.Address)
						d.run()
						d.destroy()	
					
					if has_dun and "PPPSupport" in appl.QueryPlugins():
						item = gtk.SeparatorMenuItem()
						item.show()
						serial_items.append(item)
				
						item = create_menuitem(_("Dialup Settings"), get_icon("gtk-preferences", 16))
						serial_items.append(item)
						item.show()
						self.Signals.Handle("gobject", item, "activate", open_settings, device)		
							
							
					if len(serial_items) > 1:
						sub = gtk.Menu()
						sub.show()
						
						item = create_menuitem(_("Serial Ports"), get_icon("modem", 16))
						item.set_submenu(sub)
						item.show()
						items.append((90, item))
						
						for item in serial_items:
							sub.append(item)
					
					else:
						for item in serial_items:
							items.append((80, item))

					
				elif name == "network":
					self.Signals.Handle("bluez", service, self.service_property_changed, "PropertyChanged")
					sprops = service.GetProperties()
					
					if not sprops["Connected"]:
											
						for uuid in uuids:
							uuid16 = uuid128_to_uuid16(uuid)
							if uuid16 == GN_SVCLASS_ID:
								item = create_menuitem(_("Group Network"), get_icon("network-wireless", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
								item.show()
								items.append((80, item))
						
							if uuid16 == NAP_SVCLASS_ID:
								item = create_menuitem(_("Network Access Point"), get_icon("network-wireless", 16))
								self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name, uuid)
								item.show()
								items.append((81, item))


					else:
						item = create_menuitem(_("Network"), get_x_icon("network-wireless", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
						item.show()
						items.append((101, item))
						

						if "DhcpClient" in appl.QueryPlugins():
							def renew(x):
								appl.DhcpClient(sprops["Device"])							
							item = create_menuitem(_("Renew IP Address"), get_icon("gtk-refresh", 16))
							self.Signals.Handle("gobject", item, "activate", renew)
							item.show()
							items.append((201, item))
					
				elif name == "input":
					self.Signals.Handle("bluez", service, self.service_property_changed, "PropertyChanged")
					sprops = service.GetProperties()
					if sprops["Connected"]:
						item = create_menuitem(_("Input Service"), get_x_icon("mouse", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
						items.append((100, item))

					else:
						item = create_menuitem(_("Input Service"), get_icon("mouse", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)
						items.append((1, item))
				
					item.show()
					
					
				elif name == "headset":
					sprops = service.GetProperties()
					
					if sprops["Connected"]:
						item = create_menuitem(_("Headset Service"), get_icon("blueman-handsfree", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
						items.append((110, item))
					else:
						item = create_menuitem(_("Headset Service"), get_icon("blueman-handsfree", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)
						items.append((10, item))
						
					item.show()
					
					

				elif name == "audiosink":
					sprops = service.GetProperties()
					
					if sprops["Connected"]:
						item = create_menuitem(_("Audio Sink"), get_icon("blueman-headset", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
						items.append((120, item))
					else:
						item = create_menuitem(_("Audio Sink"), get_icon("blueman-headset", 16))
						item.props.tooltip_text = _("Allows to send audio to remote device")
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)
						items.append((20, item))
						
					item.show()
					
				
				elif name == "audiosource":
					sprops = service.GetProperties()
					
					if not sprops["State"] == "disconnected":
						item = create_menuitem(_("Audio Source"), get_icon("blueman-headset", 16))
						self.Signals.Handle("gobject", item, "activate", self.on_disconnect, device, name)
						items.append((121, item))
					else:
						item = create_menuitem(_("Audio Source"), get_icon("blueman-headset", 16))
						item.props.tooltip_text = _("Allows to receive audio from remote device")
						self.Signals.Handle("gobject", item, "activate", self.on_connect, device, name)
						items.append((21, item))
					item.show()
					
			have_disconnectables = False
			have_connectables = False

			if True in map(lambda x: x[0] >= 100, items):
				have_disconnectables = True
			
			if True in map(lambda x: x[0] < 100, items):
				have_connectables = True
				
			if True in map(lambda x: x[0] >= 200, items):
				item = gtk.SeparatorMenuItem()
				item.show()
				items.append((199, item))
				
			
			if have_connectables:		
				item = gtk.MenuItem()
				label = gtk.Label()
				label.set_markup(_("<b>Connect To:</b>"))
				label.props.xalign = 0.0
			
				label.show()
				item.add(label)
				item.props.sensitive = False
				item.show()
				items.append((0, item))
				
			if have_disconnectables:		
				item = gtk.MenuItem()
				label = gtk.Label()
				label.set_markup(_("<b>Disconnect:</b>"))
				label.props.xalign = 0.0
			
				label.show()
				item.add(label)
				item.props.sensitive = False
				item.show()
				items.append((99, item))		
						
			items.sort(lambda a, b: cmp(a[0], b[0]))
			for priority, item in items:
				self.append(item)

			if items != []:
				item = gtk.SeparatorMenuItem()
				item.show()
				self.append(item)
			
			del items
			
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
			
			item = create_menuitem(_("Pair"), get_icon("gtk-dialog-authentication", 16))
			item.props.tooltip_text = _("Create pairing with the device")
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
				
				def reply():
					prog_msg(_("Success!"))
					MessageArea.close()
					
				def error(*args):
					dprint("err", args)
					prog_msg(_("Fail"))
					MessageArea.show_message(e_(str(args[0])))					
					
				prog = ManagerProgressbar(self.Blueman, False, _("Refreshing"))
				prog.start()
				self.set_op(device, _("Refreshing Services..."))
				appl.RefreshServices(device.GetObjectPath(), reply_handler=reply, error_handler=error)
			
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
			item.props.tooltip_text = _("Forcefully disconnect a device")
			
			self.append(item)
			item.show()
			
			def on_disconnect(item):
				def finished(*args):
					self.unset_op(device)

				self.set_op(device, _("Disconnecting..."))
				self.Blueman.disconnect(device, reply_handler=finished, error_handler=finished)
			
			if device.Connected:
				self.Signals.Handle(item, "activate", on_disconnect)

			else:
				item.props.sensitive = False
				


		
