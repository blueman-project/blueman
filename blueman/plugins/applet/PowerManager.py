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
import blueman.bluez as Bluez
from blueman.bluez.errors import BluezDBusException
import dbus
import types

class PowerManager(AppletPlugin):
	__depends__ = ["StatusIcon", "Menu"]
	__unloadable__ = False
	__description__ = _("Controls bluetooth adapter power states")
	__author__ = "Walmis"
	
	def on_load(self, applet):
		AppletPlugin.add_method(self.on_bluetooth_power_state_changed)
		
		self.Applet = applet
		
		self.item = create_menuitem(_("<b>Bluetooth Off</b>"), get_icon("gtk-stop", 16))
		self.item.get_child().set_markup(_("<b>Turn Bluetooth Off</b>"))
		
		self.item.props.tooltip_text = _("Turn off all adapters")
		self.item.connect("activate", lambda x: self.on_bluetooth_toggled())
		
		dbus.SystemBus().add_signal_receiver(self.adapter_property_changed, "PropertyChanged", "org.bluez.Adapter", "org.bluez", path_keyword="path")
		
		self.Applet.Plugins.Menu.Register(self, self.item, 0)
		
		self.Applet.DbusSvc.add_method(self.SetBluetoothStatus, in_signature="b", out_signature="")
		self.Applet.DbusSvc.add_method(self.GetBluetoothStatus, in_signature="", out_signature="b")
		self.BluetoothStatusChanged = self.Applet.DbusSvc.add_signal("BluetoothStatusChanged", signature="b")
		
		self.bluetooth_off = False
		self.state_change_deferred = -1
		
	def on_query_status_icon_visibility(self):
		print self

	def SetBluetoothStatus(self, status):
		self.bluetooth_off = not status
	
	def GetBluetoothStatus(self):
		if self.state_change_deferred != -1:
			return not self.state_change_deferred
		else:
			return not self.bluetooth_off
		
	def adapter_property_changed(self, key, value, path):
		if key == "Powered":
			if value and self.bluetooth_off:
				dprint("adapter powered on while in off state, turning bluetooth on")
				self.bluetooth_off = False

		
	def on_manager_state_changed(self, state):
		if state:
			adapters = self.Applet.Manager.ListAdapters()
			for adapter in adapters:
				props = adapter.GetProperties()
				if not props["Powered"]:
					self.bluetooth_off = True
					if self.state_change_deferred != -1:
						break
					else:
						return
			
			if self.state_change_deferred != -1:
				self.bluetooth_off = self.state_change_deferred
				self.state_change_deferred = -1
	
	def on_bluetooth_toggled(self):
		self.bluetooth_off = not self.bluetooth_off
		
	def on_status_icon_pixbuf_ready(self, pixbuf):
		opacity = 255 if self.GetBluetoothStatus() else 100
		self.Applet.Plugins.StatusIcon.set_from_pixbuf( opacify_pixbuf(pixbuf, opacity) )
		return True
		
	def on_adapter_added(self, path):
		adapter = Bluez.Adapter(path)
		def on_ready():
			if self.bluetooth_off:
				adapter.SetProperty("Powered", False)
			else:
				adapter.SetProperty("Powered", True)				
		
		wait_for_adapter(adapter, on_ready)

	
		
	
	def __setattr__(self, key, value):
		if key == "bluetooth_off":
			dprint("bt_off", value)
			dprint("manager state", self.Applet.Manager)
				
			def set_global_state():
				if key in self.__dict__:
					dprint("off", self.__dict__[key], value)
					adapters = self.Applet.Manager.ListAdapters()
					for adapter in adapters:
						adapter.SetProperty("Powered", not value)
		
			
			def error(e):
				d = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_CLOSE, message_format=None)
				
				d.props.text = _("Failed to set bluetooth power")
				d.props.secondary_text = _("The error reported is: %s") % str(e)
				d.props.icon_name = "blueman"
				d.run()
				d.destroy()
			
			if not key in self.__dict__:
				self.__dict__[key] = value
			
			if not self.Applet.Manager:
				self.state_change_deferred = value
				return
			
			if self.__dict__[key] != value:
				self.__dict__[key] = value
									
				if value:
					try:
						set_global_state()
					except BluezDBusException, e:	
						error(e)
						return
				
					self.item.get_child().set_markup(_("<b>Turn Bluetooth On</b>"))
					self.item.set_image(gtk.image_new_from_pixbuf(get_icon("gtk-yes", 16)))
					self.BluetoothStatusChanged(False)
					self.Applet.Plugins.Run("on_bluetooth_power_state_changed", False)
					if self.Applet.Plugins.StatusIcon.pixbuf:
						self.Applet.Plugins.StatusIcon.set_from_pixbuf( opacify_pixbuf(self.Applet.Plugins.StatusIcon.pixbuf, 100) )
				else:
					self.item.get_child().set_markup(_("<b>Turn Bluetooth Off</b>"))
					self.item.set_image(gtk.image_new_from_pixbuf(get_icon("gtk-stop", 16)))
					self.BluetoothStatusChanged(True)
					self.Applet.Plugins.Run("on_bluetooth_power_state_changed", True)
					try:
						set_global_state()
					except BluezDBusException, e:	
						error(e)
						self.bluetooth_off = True
						return
					
					if self.Applet.Plugins.StatusIcon.pixbuf:
						self.Applet.Plugins.StatusIcon.set_from_pixbuf( opacify_pixbuf(self.Applet.Plugins.StatusIcon.pixbuf, 255) )
		else:				
			self.__dict__[key] = value
		
	def on_bluetooth_power_state_changed(*args):
		pass
