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

from blueman.plugins.AppletPlugin import AppletPlugin
import dbus
from gi.repository import GObject
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.Notification import Notification
from blueman.Sdp import *
from blueman.Functions import get_icon, composite_icon
import weakref

class ConnectionHandler:
	def __init__(self, parent, device, uuid, reply, err):
		self.parent = parent
		self.device = device
		self.uuid = uuid
		self.reply = reply
		self.err = err
		self.rfcomm_dev = None
		self.timeout = None
		
		self.signals = SignalTracker()
		self.signals.Handle("dbus", self.parent.bus, 
				    self.on_mm_device_added, 
				    "DeviceAdded", 
				    "org.freedesktop.ModemManager")
				    
		#for some reason these handlers take a reference and don't give it back
		#so i have to workaround :(
		w = weakref.ref(self)
		device.Services["serial"].Connect(uuid, 
						  reply_handler=lambda *args: w() and w().on_connect_reply(*args), 
						  error_handler=lambda *args: w() and w().on_connect_error(*args))
		
	def __del__(self):
		dprint("deleting")
		
	def on_connect_reply(self, rfcomm):
		self.rfcomm_dev = rfcomm
		self.timeout = GObject.timeout_add(10000, self.on_timeout)
		
	def on_connect_error(self, *args):
		self.err(*args)
		self.cleanup()
		
	def cleanup(self):
		if self.timeout:
			GObject.source_remove(self.timeout)
		self.signals.DisconnectAll()
		
		del self.device
		
	def on_mm_device_added(self, path):
		dprint(path)
		props = self.parent.bus.call_blocking("org.freedesktop.ModemManager", 
						path, 
						"org.freedesktop.DBus.Properties", 
						"GetAll", 
						"s", 
						["org.freedesktop.ModemManager.Modem"])
						
		if self.rfcomm_dev and props["Driver"] == "bluetooth" and props["Device"] in self.rfcomm_dev:
			dprint("It's our bluetooth modem!")
			
			modem = get_icon("modem", 24)
			blueman = get_icon("blueman", 48)
			
			icon = composite_icon(blueman, [(modem, 24, 24, 255)])
			
			Notification(_("Bluetooth Dialup"), 
				     _("DUN connection on %s will now be available in Network Manager") % self.device.Alias, 
				     pixbuf=icon,
				     status_icon=self.parent.Applet.Plugins.StatusIcon)
				     
			self.reply(self.rfcomm_dev)
			self.cleanup()

			
	def on_timeout(self):
		self.timeout = None
		self.err(dbus.DBusException(_("Modem Manager did not support the connection")))
		self.cleanup()

class NMDUNSupport(AppletPlugin):
	__depends__ = ["StatusIcon", "DBusService"]
	__conflicts__ = ["PPPSupport", "NMIntegration"]
	__icon__ = "modem"
	__author__ = "Walmis"
	__description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager 0.8")
	__priority__ = 1
	
	def on_load(self, applet):
		self.bus = dbus.SystemBus()
		
	def on_unload(self):
		pass
		
	def rfcomm_connect_handler(self, device, uuid, reply, err):
		uuid16 = sdp_get_serial_type(device.Address, uuid)
		if DIALUP_NET_SVCLASS_ID in uuid16:		

			ConnectionHandler(self, device, uuid, reply, err)
		
			return True
		else:
			return False

