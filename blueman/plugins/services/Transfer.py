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
from blueman.Constants import *
from blueman.plugins.ServicePlugin import ServicePlugin

from blueman.main.AppletService import AppletService
from blueman.main.Config import Config
from blueman.Functions import dprint


class Transfer(ServicePlugin):
	__plugin_info__ = (_("Transfer"), "gtk-open")
	def on_load(self, container):
		
		self.Builder = Gtk.Builder()
		self.Builder.set_translation_domain("blueman")
		self.Builder.add_from_file(UI_PATH +"/services-transfer.ui")
		self.widget = self.Builder.get_object("transfer")
		
		self.ignored_keys = []
		
		container.pack_start(self.widget, True, True, 0)
		a = AppletService()
		if "TransferService" in a.QueryPlugins():
			self.setup_transfer()
		else:
			self.widget.props.sensitive = False
			self.widget.props.tooltip_text = _("Applet's transfer service plugin is disabled")
		
		return True
		
	def on_enter(self):
		self.widget.props.visible = True
		
	def on_leave(self):
		self.widget.props.visible = False

	def on_property_changed(self, config, key, value):

		if key == "opp_enabled":
			self.Builder.get_object(key).props.active = value
		if key == "ftp_enabled":
			self.Builder.get_object(key).props.active = value
		if key == "ftp_allow_write":
			self.Builder.get_object(key).props.active = value
		if key == "shared_path":
			self.Builder.get_object(key).set_current_folder(value)
		if key == "browse_command":
			return
		if key == "shared_path":
			self.option_changed_notify(key, False)
		else:
			self.option_changed_notify(key)
	
	def on_apply(self):
		if self.on_query_apply_state() == True:

			try:
				a = AppletService()
			except:
				dprint("failed to connect to applet")
			else:
				c = self.get_options()
				if "opp_enabled" in c:
					if not self.TransConf.props.opp_enabled:
						a.TransferControl("opp", "destroy")
				
				if "ftp_enabled" in c:
					if not self.TransConf.props.ftp_enabled:
						a.TransferControl("ftp", "destroy")
				
				
				if "opp_accept" in c or "shared_path" in c or "opp_enabled" in c:
					if self.TransConf.props.opp_enabled:
						state = a.TransferStatus("opp")
						if state == 0: #destroyed
							a.TransferControl("opp", "create")
						elif state == 2: #running
							a.TransferControl("opp", "stop")
							a.TransferControl("opp", "start")
						elif state == 1:
							a.TransferControl("opp", "start")
							
				
				if "ftp_allow_write" in c or "shared_path" in c or "ftp_enabled" in c:
					if self.TransConf.props.ftp_enabled:
						state = a.TransferStatus("ftp")
						if state == 0: #destroyed
							a.TransferControl("ftp", "create")
						elif state == 2: #running
							a.TransferControl("ftp", "stop")
							a.TransferControl("ftp", "start")
						elif state == 1:
							a.TransferControl("ftp", "start")
				

				self.clear_options()
				
				
			dprint("transfer apply")


	
	def on_query_apply_state(self):
		opts = self.get_options()
		if opts == []:
			return False
		else:
			return True

			
	def setup_transfer(self):
		a = AppletService()
		status = a.TransferStatus("opp")
		if status == -1:
			self.widget.props.sensitive = False
			self.widget.props.tooltip_text = _("obex-data-server not available")
		
		self.TransConf = Config("transfer")
		self.TransConf.connect("property-changed", self.on_property_changed)
		opp_enabled = self.Builder.get_object("opp_enabled")
		ftp_enabled = self.Builder.get_object("ftp_enabled")
		ftp_allow_write = self.Builder.get_object("ftp_allow_write")
		opp_accept = self.Builder.get_object("opp_accept")
		shared_path = self.Builder.get_object("shared_path")
		obex_cmd = self.Builder.get_object("e_obex_cmd")
	
		opp_enabled.props.active = self.TransConf.props.opp_enabled
		ftp_enabled.props.active = self.TransConf.props.ftp_enabled
		ftp_allow_write.props.active = self.TransConf.props.ftp_allow_write
		opp_accept.props.active = self.TransConf.props.opp_accept
		if self.TransConf.props.browse_command == None:
			self.TransConf.props.browse_command = DEF_BROWSE_COMMAND
		
		obex_cmd.props.text = self.TransConf.props.browse_command
		
		if self.TransConf.props.shared_path != None:
			shared_path.set_current_folder(self.TransConf.props.shared_path)
		
		obex_cmd.connect("changed", lambda x: setattr(self.TransConf.props, "browse_command", x.props.text))
		opp_enabled.connect("toggled", lambda x: setattr(self.TransConf.props, "opp_enabled", x.props.active))
		ftp_enabled.connect("toggled", lambda x: setattr(self.TransConf.props, "ftp_enabled", x.props.active))
		ftp_allow_write.connect("toggled", lambda x: setattr(self.TransConf.props, "ftp_allow_write", x.props.active))
		opp_accept.connect("toggled", lambda x: setattr(self.TransConf.props, "opp_accept", x.props.active))
		shared_path.connect("current-folder-changed", lambda x: setattr(self.TransConf.props, "shared_path", x.get_filename()))

