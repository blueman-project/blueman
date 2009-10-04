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
from blueman.main.applet.BluezAgent import AdapterAgent

from blueman.bluez.Device import Device as BluezDevice
from blueman.main.Device import Device
from blueman.main.applet.BluezAgent import TempAgent
from blueman.bluez.Adapter import Adapter

import gobject
import gtk
import dbus

class DBusService(AppletPlugin):
	__depends__ = ["StatusIcon"]
	__unloadable__ = False
	__description__ = _("Provides DBus API for other Blueman components")
	__author__ = "Walmis"

	def on_load(self, applet):
		self.Applet = applet
		
		AppletPlugin.add_method(self.on_rfcomm_connected)
		AppletPlugin.add_method(self.on_rfcomm_disconnect)
		AppletPlugin.add_method(self.rfcomm_connect_handler)
		AppletPlugin.add_method(self.service_connect_handler)
		
		self.add_dbus_method(self.ServiceProxy, in_signature="sosas", async_callbacks=("ok","err"))
		self.add_dbus_method(self.CreateDevice, in_signature="ssbu", async_callbacks=("ok","err"))
		self.add_dbus_method(self.CancelDeviceCreation, in_signature="ss", async_callbacks=("ok","err"))
		self.add_dbus_method(self.RfcommConnect, in_signature="ss", out_signature="s", async_callbacks=("ok","err"))
		self.add_dbus_method(self.RfcommDisconnect, in_signature="ss", out_signature="")
		
		self.add_dbus_method(self.QueryPlugins, in_signature="", out_signature="as")
		self.add_dbus_method(self.QueryAvailablePlugins, in_signature="", out_signature="as")
		self.add_dbus_method(self.SetPluginConfig, in_signature="sb", out_signature="")
		
	def QueryPlugins(self):
		return self.Applet.Plugins.GetLoaded()
		
	def QueryAvailablePlugins(self):
		return self.Applet.Plugins.GetClasses()
		
	def SetPluginConfig(self, plugin, value):
		self.Applet.Plugins.SetConfig(plugin, value)
	
	def ServiceProxy(self, interface, object_path, _method, args, ok, err):
		bus = dbus.SystemBus()
		service = bus.get_object("org.bluez", object_path)
		method = service.get_dbus_method(_method, interface)
		
		
		if _method == "Connect":
			dev = Device(BluezDevice(object_path))
			try:
				self.Applet.Plugins.RecentConns.notify(dev, interface, args )
			except KeyError:
				dprint("RecentConns plugin is unavailable")
		
		self.handled = False
		def cb(inst, ret):
			if ret == True:
				self.handled = True
				#stop further execution
				raise StopException
		
		self.Applet.Plugins.RunEx("service_connect_handler", cb, interface, object_path, _method, args, ok, err)

		if not self.handled:
			method(reply_handler=ok, error_handler=err, *args)
			
		del self.handled
		
	def service_connect_handler(self, interface, object_path, _method, args, ok, err):
		pass

	def CreateDevice(self, adapter_path, address, pair, time, ok, err):
		if self.Applet.Manager:
			adapter = Adapter(adapter_path)

			if pair:
				agent_path = "/org/blueman/agent/temp/"+address.replace(":", "")
				agent = TempAgent(self.Applet.Plugins.StatusIcon, agent_path, time)
				adapter.GetInterface().CreatePairedDevice(address, agent_path, "DisplayYesNo", error_handler=err, reply_handler=ok, timeout=120)
				
			else:
				adapter.GetInterface().CreateDevice(address, error_handler=err, reply_handler=ok, timeout=120)
				
		else:
			err()
	
	def CancelDeviceCreation(self, adapter_path, address, ok, err):
		if self.applet.Manager:
			adapter = Adapter(adapter_path)

			adapter.GetInterface().CancelDeviceCreation(address, error_handler=err, reply_handler=ok)
				
		else:
			err()

	def RfcommConnect(self, device, uuid, ok, err):
		def reply(rfcomm):
			self.Applet.Plugins.Run("on_rfcomm_connected", dev, rfcomm, uuid)
			ok(rfcomm)

		dev = Device(BluezDevice(device))
		try:
			self.Applet.Plugins.RecentConns.notify(dev.Copy(), "org.bluez.Serial", [uuid] )
		except KeyError:
			pass
			
		rets = self.Applet.Plugins.Run("rfcomm_connect_handler", dev, uuid, reply, err)
		if True in rets:
			pass
		else:
			dprint("No handler registered")
			err(dbus.DBusException("Service not supported\nPossibly the plugin that handles this service is not loaded"))
		
		
		#dev.Services["serial"].Connect(uuid, reply_handler=reply, error_handler=err)
		#dprint("Connecting rfcomm device")
		
		
	def rfcomm_connect_handler(self, device, uuid, reply_handler, error_handler):
		return False
		
		
	def RfcommDisconnect(self, device, rfdevice):
		dev = Device(BluezDevice(device))
		dev.Services["serial"].Disconnect(rfdevice)
		
		self.Applet.Plugins.Run("on_rfcomm_disconnect", rfdevice)
		
		dprint("Disonnecting rfcomm device")
		
	def on_rfcomm_connected(self, device, port, uuid):
		pass
		
	def on_rfcomm_disconnect(self, port):
		pass
