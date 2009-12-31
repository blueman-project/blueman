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
# NMMonitor: Monitors a selected device and emits a signal when it was disconnected via NetworkManager
import gobject
import dbus
from blueman.Functions import *

from blueman.main.SignalTracker import SignalTracker
from blueman.plugins.AppletPlugin import AppletPlugin


NM_DEVICE_STATE_UNKNOWN = 0,

#/* Initial state of all devices and the only state for devices not
# * managed by NetworkManager.
# *
# * Allowed next states:
# *   UNAVAILABLE:  the device is now managed by NetworkManager
# */
NM_DEVICE_STATE_UNMANAGED = 1

#/* Indicates the device is not yet ready for use, but is managed by
# * NetworkManager.  For Ethernet devices, the device may not have an
# * active carrier.  For WiFi devices, the device may not have it's radio
# * enabled.
# *
# * Allowed next states:
# *   UNMANAGED:  the device is no longer managed by NetworkManager
# *   DISCONNECTED:  the device is now ready for use
# */
NM_DEVICE_STATE_UNAVAILABLE = 2

#/* Indicates the device does not have an activate connection to anything.
# *
# * Allowed next states:
# *   UNMANAGED:  the device is no longer managed by NetworkManager
# *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
# *   PREPARE:  the device has started activation
# */
NM_DEVICE_STATE_DISCONNECTED = 3

#/* Indicate states in device activation.
# *
# * Allowed next states:
# *   UNMANAGED:  the device is no longer managed by NetworkManager
# *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
# *   FAILED:  an error ocurred during activation
# *   NEED_AUTH:  authentication/secrets are needed
# *   ACTIVATED:  (IP_CONFIG only) activation was successful
# *   DISCONNECTED:  the device's connection is no longer valid, or NetworkManager went to sleep
# */
NM_DEVICE_STATE_PREPARE = 4
NM_DEVICE_STATE_CONFIG = 5
NM_DEVICE_STATE_NEED_AUTH = 6
NM_DEVICE_STATE_IP_CONFIG = 7

#/* Indicates the device is part of an active network connection.
# *
# * Allowed next states:
# *   UNMANAGED:  the device is no longer managed by NetworkManager
# *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
# *   FAILED:  a DHCP lease was not renewed, or another error
# *   DISCONNECTED:  the device's connection is no longer valid, or NetworkManager went to sleep
# */
NM_DEVICE_STATE_ACTIVATED = 8

#/* Indicates the device's activation failed.
# *
# * Allowed next states:
# *   UNMANAGED:  the device is no longer managed by NetworkManager
# *   UNAVAILABLE:  the device is no longer ready for use (rfkill, no carrier, etc)
# *   DISCONNECTED:  the device's connection is ready for activation, or NetworkManager went to sleep
# */
NM_DEVICE_STATE_FAILED = 9

if not HAL_ENABLED:
	raise ImportError("NMMonitor (deprecated) requires hal support")


class NMMonitor(AppletPlugin, gobject.GObject):
	__gsignals__ = {
		#args: udi
		'disconnected' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
		#args: udi
		'modem-removed' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_STRING,)),
		#args: udi, bdaddr
		'modem-added' : (gobject.SIGNAL_NO_HOOKS, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING,)),
	}
	
	__icon__ = "network"
	__description__ = _("Monitors NetworkManager's modem connections and automatically disconnects Bluetooth link after the network connection is closed")
	__author__ = "Walmis"
	
	def on_load(self, applet):
		gobject.GObject.__init__(self)

		self.bus = dbus.SystemBus()
		obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
		
		self.hal_mgr = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')
		
		self.monitored_udis = []
		
		self.signals = SignalTracker()
		
		
		self.signals.Handle("dbus", self.bus, self.on_device_state_changed, "StateChanged", "org.freedesktop.NetworkManager.Device", path_keyword="udi")
		self.signals.Handle("dbus", self.bus, self.on_device_added, "DeviceAdded", "org.freedesktop.Hal.Manager")
		self.signals.Handle("dbus", self.bus, self.on_device_removed, "DeviceRemoved", "org.freedesktop.Hal.Manager")
#		self.signals.Handle("bluez", device.Device, self.on_device_propery_changed, "PropertyChanged")
		
	def on_unload(self):
		self.signals.DisconnectAll()	
	
	def on_device_removed(self, udi):
		if udi in self.monitored_udis:
			self.monitored_udis.remove(udi)
			self.emit("modem-removed", udi)
		
	def on_device_added(self, udi):
		obj = self.bus.get_object('org.freedesktop.Hal', udi)
		device = dbus.Interface(obj, 'org.freedesktop.Hal.Device')		
		try:
			if device.QueryCapability("modem") and device.GetPropertyString("info.linux.driver") == "rfcomm":
				self.monitored_udis.append(udi)
				self.emit("modem-added", udi, device.GetPropertyString("info.bluetooth_address"))
		except:
			pass
						
	def on_device_state_changed(self, state, prev_state, reason, udi):
		if udi in self.monitored_udis:
			dprint("state=%u prev_state=%u reason=%u" % (state, prev_state, reason))
			if state <= 3 and 3 < prev_state <= 8:
				self.emit("disconnected", udi)
						
