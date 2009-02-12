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

import gtk
import gettext
from blueman.Constants import *
from blueman.Functions import setup_icon_path
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.AppletService import AppletService
from blueman.main.Config import Config

_ = gettext.gettext

class Headset(ServicePlugin):
	__plugin_info__ = (_("Headset"), "blueman-headset")
	def on_load(self, container):
		
		self.Builder = gtk.Builder()
		self.Builder.set_translation_domain("blueman")
		self.Builder.add_from_file(UI_PATH +"/services-headset.ui")
		self.widget = self.Builder.get_object("headset")
		
		container.pack_start(self.widget)
		self.setup_headset()
		
		return (_("Headset"), "blueman-headset")
		
	def on_enter(self):
		self.widget.props.visible = True
		
	def on_leave(self):
		self.widget.props.visible = False

	def on_property_changed(self, config, key, value):
		if key == "command":
			self.Builder.get_object(key).props.text = value

			
	def setup_headset(self):

		self.Conf = Config("headset")
		self.Conf.connect("property-changed", self.on_property_changed)
		command = self.Builder.get_object("command")

		if self.Conf.props.command:
			command.props.text = self.Conf.props.command
		command.connect("changed", lambda x: setattr(self.Conf.props, "command", x.props.text))


