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
from blueman.Constants import HAL_ENABLED

if not HAL_ENABLED:
	raise ImportError("Hal disabled")

class Hal(MechanismPlugin):
	def on_load(self):
		self.add_dbus_method(self.HalRegisterModemPort, in_signature="ss", out_signature="", async_callbacks=("ok", "err"))
		self.add_dbus_method(self.HalUnregisterModemPortAddr, in_signature="s", out_signature="")
		self.add_dbus_method(self.HalUnregisterModemPortDev, in_signature="s", out_signature="")
		self.add_dbus_method(self.HalRegisterNetDev, in_signature="s", out_signature="")
		
	def HalRegisterModemPort(self, rfcomm_device, bd_addr, ok, err):
		from blueman.main.HalManager import HalManager
		self.timer.reset()
		halmgr = HalManager()
		dprint("** Registering modem")
		halmgr.register(rfcomm_device, bd_addr, ok, err)

	def HalUnregisterModemPortAddr(self, address):
		from blueman.main.HalManager import HalManager
		self.timer.reset()
		halmgr = HalManager()
		dprint("** Unregistering modem")
		halmgr.unregister_addr(address)
		
	def HalUnregisterModemPortDev(self, rfcomm_device):
		from blueman.main.HalManager import HalManager
		self.timer.reset()
		halmgr = HalManager()
		dprint("** Unregistering modem")
		halmgr.unregister_dev(rfcomm_device)

	def HalRegisterNetDev(self, devicename):
		from blueman.main.HalManager import HalManager
		self.timer.reset()
		halmgr = HalManager()
		halmgr.register_netdev(devicename)
