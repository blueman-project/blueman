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

from gi.repository import Gtk
import dbus
from blueman.Constants import *
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.AppletService import AppletService
from blueman.main.BluezConfig import BluezConfig
from blueman.main.Config import Config
from blueman.Functions import dprint
from blueman.main.Mechanism import Mechanism


class Audio(ServicePlugin):
	__plugin_info__ = (_("Audio"), "audio-card")
	def on_load(self, container):
		
		self.Builder = Gtk.Builder()
		self.Builder.set_translation_domain("blueman")
		self.Builder.add_from_file(UI_PATH +"/services-audio.ui")
		self.widget = self.Builder.get_object("audio")
		
		self.ignored_keys = []
		
		container.pack_start(self.widget, True, True, 0)
		
		self.cb_a2dp = self.Builder.get_object("a2dp")
		self.cb_hsp = self.Builder.get_object("hsp")
		
		self.info = self.Builder.get_object("info")
		
		c = BluezConfig("audio.conf")
		try:
			opt = c.get("General", "Enable")
			opt = opt.split(",")
			if "Source" in opt:
				self.cb_a2dp.props.active = True
			if "Gateway" in opt:
				self.cb_hsp.props.active = True
		except:
			pass
		
		self.cb_a2dp.connect("toggled", self.on_cfg_changed)
		self.cb_hsp.connect("toggled", self.on_cfg_changed)
		
		return True
		
	def on_enter(self):
		self.widget.props.visible = True
		
	def on_leave(self):
		self.widget.props.visible = False

	
	def on_apply(self):
		if self.get_options() != []:
			vals = ["Sink"]
			if self.cb_a2dp.props.active:
				vals.append("Source")
			if self.cb_hsp.props.active:
				vals.append("Gateway")
			try:
				m = Mechanism()
				m.SetBluezConfig("audio.conf", "General", "Enable", ",".join(vals))
				m.SaveBluezConfig("audio.conf")
				m.RestartBluez()
			except dbus.DBusException, e:
				dprint(e)
			else:
				self.clear_options()
		
	def on_cfg_changed(self, cb):
		self.option_changed_notify(cb)

	
	def on_query_apply_state(self):
		opts = self.get_options()
		if opts == []:
			self.info.props.visible = False
			return False
		else:
			self.info.props.visible = True
			return True

