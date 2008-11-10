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
import dbus
import dbus.glib
import dbus.service
import os.path
import blueman.bluez as Bluez
import gettext
_ = gettext.gettext

class BluezAgent(dbus.service.Object):
	
	class AgentErrorRejected(dbus.DBusException):
		def __init__(self)
			dbus.DBusException.__init__(self, name='org.bluez.Error.Rejected')
	
	class AgentErrorCanceleed(dbus.DBusException):
		def __init__(self)
			dbus.DBusException.__init__(self, name='org.bluez.Error.Canceled')
	
	def __init__(self, applet, adapter):
		self.applet = applet
		self.adapter = adapter
		self.dialog = None
		self.bus = dbus.SessionBus();
		self.bus.request_name("org.blueman.Applet")
		adapter_name = os.path.basename(adapter)
		dbus.service.Object.__init__(self, self.bus, "/org/blueman/agent/"+adapter_name)
		
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="", out_signature="")
	def Release(self):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="o", out_signature="s", async_callbacks=("ok","err"))
	def RequestPinCode(self, device_path, ok, err):
		device = Bluez.Device(device_path)
		address = device.Address
		name = device.Name
		alias = address
		if name:
			alias = "%s (%s)" % (name, address)
		message = _('Pairing request for %s') % (alias)
		
		if self.dialog:
			raise AgentErrorCanceled
		self.dialog = self.applet.build_blah_dialog()
		if not self.dialog:
			raise AgentErrorCanceled
		
		self.applet.show_notification(_('Bluetooth device'), message, 0,
									_('Enter PIN code'), self.on_notification_close)
		
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="o", out_signature="u", async_callbacks=("ok","err"))
	def RequestPasskey(self, device, ok, err):
		ok(0)
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="ouy", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="ou", out_signature="", async_callbacks=("ok","err"))
	def RequestConfirmation(self, device, passkey, ok, err):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="os", out_signature="", async_callbacks=("ok","err"))
	def Authorize(self, device, uuid, ok, err):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="s", out_signature="", async_callbacks=("ok","err"))
	def ConfirmModeChange(self, mode, ok, err):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="", out_signature="")
	def Cancel(self):
		pass

