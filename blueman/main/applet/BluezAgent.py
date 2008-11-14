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
import gtk
import blueman.bluez as Bluez
import gettext
_ = gettext.gettext

class AgentErrorRejected(dbus.DBusException):
	def __init__(self):
		dbus.DBusException.__init__(self, name='org.bluez.Error.Rejected')

class AgentErrorCanceled(dbus.DBusException):
	def __init__(self):
		dbus.DBusException.__init__(self, name='org.bluez.Error.Canceled')

class BluezAgent(dbus.service.Object):
	
	def __init__(self, applet, adapter):
		self.applet = applet
		self.adapter = adapter
		self.dialog = None
		self.bus = dbus.SystemBus();
		adapter_name = os.path.basename(adapter)
		self.dbus_path = "/org/blueman/agent/"+adapter_name
		dbus.service.Object.__init__(self, self.bus, self.dbus_path)
		
	def __del__(self):
		print 'Agent on path', self.dbus_path, 'deleted'
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="", out_signature="")
	def Release(self):
		self.Cancel()
		self.remove_from_connection()
	
	def on_notification_close(self, n, action):
		self.dialog.show()
		self.applet.status_icon.set_blinking(False)
	
	def passkey_dialog_cb(self, dialog, response_id, is_numeric, ok, err):
		if response_id == gtk.RESPONSE_ACCEPT:
			ret = self.pin_entry.get_text()
			if is_numeric:
				ret = int(ret)
			ok(ret)
		else:
			err(AgentErrorRejected())
		dialog.destroy()
		self.dialog = None
		
	def auth_dialog_cb(self, dialog, response_id, device_path, ok, err):
		if response_id == gtk.RESPONSE_YES:
			if self.always_grant.props.active:
				device = Bluez.Device(device_path)
				device.SetProperty("Trusted", True)
			ok()
		else:
			err(AgentErrorRejected())
		dialog.destroy()
		self.dialog = None
	
	def get_device_alias(self, device_path):
		device = Bluez.Device(device_path)
		props = device.GetProperties()
		address = props['Address']
		name = props['Name']
		alias = address
		if name:
			alias = "%s (%s)" % (name, address)
		return alias
	
	def passkey_common(self, device_path, dialog_msg, notify_msg, is_numeric, ok, err):
		alias = self.get_device_alias(device_path)
		notify_message = _('Pairing request for %s') % (alias)
		
		if self.dialog:
			print 'Agent: Another dialog still active, cancelling'
			raise AgentErrorCanceled
		
		self.dialog, self.pin_entry = self.applet.build_passkey_dialog(alias, dialog_msg, is_numeric)
		if not self.dialog:
			print 'Agent: Failed to build dialog'
			raise AgentErrorCanceled
		
		self.n = self.applet.show_notification(_('Bluetooth device'), notify_message, 0,
										[[notify_msg, self.on_notification_close]])
		self.applet.status_icon.set_blinking(True)
		self.dialog.connect('response', self.passkey_dialog_cb, is_numeric, ok, err)
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="o", out_signature="s", async_callbacks=("ok","err"))
	def RequestPinCode(self, device, ok, err):
		print 'Agent.RequestPinCode'
		dialog_msg = _('Enter PIN code for authentication:')
		notify_msg = _('Enter PIN code')
		self.passkey_common(device, dialog_msg, notify_msg, False, ok, err)
		
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="o", out_signature="u", async_callbacks=("ok","err"))
	def RequestPasskey(self, device, ok, err):
		print 'Agent.RequestPasskey'
		dialog_msg = _('Enter passkey for authentication:')
		notify_msg = _('Enter passkey')
		self.passkey_common(device, dialog_msg, notify_msg, True, ok, err)
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="ouy", out_signature="")
	def DisplayPasskey(self, device, passkey, entered):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="ou", out_signature="", async_callbacks=("ok","err"))
	def RequestConfirmation(self, device, passkey, ok, err):
		pass
	
	def on_auth_always_accept(self, n, action):
		device = Bluez.Device(self.auth_dev_path)
		device.SetProperty("Trusted", True)
		self.on_auth_accept(n, action)
		
	def on_auth_accept(self, n, action):
		self.applet.status_icon.set_blinking(False)
		self.auth_ok_cb()
		self.auth_dev_path = None
		self.auth_ok_cb = None
		self.auth_err_cb = None
		
	def on_auth_deny(self, n, action):
		self.applet.status_icon.set_blinking(False)
		self.auth_err_cb(AgentErrorRejected())
		self.auth_dev_path = None
		self.auth_ok_cb = None
		self.auth_err_cb = None
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="os", out_signature="", async_callbacks=("ok","err"))
	def Authorize(self, device, uuid, ok, err):
		print 'Agent.Authorize'
		alias = self.get_device_alias(device)
		notify_message = _('Authorization request for %s') % (alias)
		action_always_accept = [_('Always accept'), self.on_auth_always_accept]
		action_accept = [_('Accept'), self.on_auth_accept]
		action_deny = [_('Deny'), self.on_auth_deny]
		
		self.auth_dev_path = device
		self.auth_ok_cb = ok
		self.auth_err_cb = err
		self.n = self.applet.show_notification(_('Bluetooth device'), notify_message, 0,
										[action_always_accept, action_accept, action_deny])
		self.applet.status_icon.set_blinking(True)
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="s", out_signature="", async_callbacks=("ok","err"))
	def ConfirmModeChange(self, mode, ok, err):
		pass
	
	@dbus.service.method(dbus_interface='org.bluez.Agent', in_signature="", out_signature="")
	def Cancel(self):
		if self.dialog:
			self.dialog.response(gtk.RESPONSE_REJECT)

