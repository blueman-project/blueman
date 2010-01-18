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
from blueman.main.Config import Config
from blueman.plugins.AppletPlugin import AppletPlugin
import dbus

class Headset(AppletPlugin):
	__author__ = "Walmis"
	__description__ = _("Runs a command when answer button is pressed on a headset")
	__icon__ = "blueman-headset"
	
	__options__  = {
		"command" : {"type": str,
				  "default": "",
				  "name": _("Command"),
				  "desc": _("Command to execute when answer button is pressed:")
				  }
	}
		
	def on_load(self, applet):
		self.bus = dbus.SystemBus()
		self.bus.add_signal_receiver(self.on_answer_requested, "AnswerRequested", "org.bluez.Headset")
		
	def on_unload(self):
		self.bus.remove_signal_receiver(self.on_answer_requested, "AnswerRequested", "org.bluez.Headset")
		
	def on_answer_requested(self):
		c = self.get_option("command")
		if c and c != "":
			args = c.split(" ")
			try:
				spawn(args, True)
			except:
				dprint("Cannot launch command")


