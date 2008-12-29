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
from blueman.Functions import dprint
from blueman.main.SignalTracker import SignalTracker


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


class NMMonitor(gobject.GObject):
	__gsignals__ = {
		'disconnected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_BOOLEAN,)),
	}
	
	def __init__(self, device, rfcomm_node):
		gobject.GObject.__init__(self)
		dprint(device, rfcomm_node)
		self.bus = dbus.SystemBus()
		obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
		
		hal_mgr = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')

		existing = hal_mgr.FindDeviceStringMatch("serial.device", rfcomm_node)
		if len(existing) > 0:
			udi = existing[0]
		else:
			return
			
		try:
			obj = self.bus.get_object('org.freedesktop.NetworkManager', udi)
			self.nm_iface = dbus.Interface(obj, 'org.freedesktop.NetworkManager.Device')
		except:
			return
		
		self.signals = SignalTracker()
		self.signals.Handle("dbus", self, 
						self.on_device_state_changed, 
						"StateChanged",
						"org.freedesktop.NetworkManager.Device",
						path=udi)
						
		self.signals.Handle("bluez", device.Device, self.on_device_propery_changed, "PropertyChanged")
		
	def on_device_propery_changed(self, key, value):
		if key == "Connected" and not value:
			self.signals.DisconnectAll()
			self.emit("disconnected", True)
						
	def on_device_state_changed(self, state, prev_state, reason):
		dprint("state=%u prev_state=%u reason=%u" % (state, prev_state, reason))
		if state <= 3 and 3 < prev_state <= 8:
			self.signals.DisconnectAll()
			self.emit("disconnected", False)
						
