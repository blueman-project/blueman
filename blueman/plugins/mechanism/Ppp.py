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
# 

from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
import dbus

class Ppp(MechanismPlugin):
	def on_load(self):
		self.add_dbus_method(self.PPPConnect, in_signature="sss", out_signature="s", sender_keyword="caller", async_callbacks=("ok", "err"))

	def ppp_connected(self, ppp, port, ok, err):
		ok(port)
		self.timer.resume()
		
	def ppp_error(self, ppp, message, ok, err):
		err(dbus.DBusException(message))
		self.timer.resume()
	
	def PPPConnect(self, port, number, apn, caller, ok, err):
		self.timer.stop()
		from blueman.main.PPPConnection import PPPConnection

		ppp = PPPConnection(port, number, apn)
		ppp.connect("error-occurred", self.ppp_error, ok, err)
		ppp.connect("connected", self.ppp_connected, ok, err)
		
		ppp.Connect()
