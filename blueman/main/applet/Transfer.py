# coding=utf-8
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
from blueman.main.SpeedCalc import SpeedCalc
from blueman.main.Config import Config
from blueman.ods.OdsManager import OdsManager
from blueman.main.Device import Device
from blueman.Functions import *
import os
import pynotify
import gettext
import gobject
from blueman.gui.Notification import Notification

_ = gettext.gettext

class Transfer(OdsManager):

	def __init__(self, applet):
		OdsManager.__init__(self)
		self.Applet = applet
		self.GHandle("server-created", self.on_server_created)
		self.transfers = {}
		self.Config = Config("transfer")
		
		#check options
		if self.Config.props.opp_enabled == None:
			self.Config.props.opp_enabled = True
		
		if self.Config.props.ftp_enabled == None:
			self.Config.props.ftp_enabled = True
			
		self.create_server("opp")
		self.create_server("ftp")
		
		self.allowed_devices = []
		
	def __del__(self):
		print "deleting transfer"

		
	def create_server(self, pattern):

		if pattern == "opp":
			if self.Config.props.opp_enabled:
				OdsManager.create_server(self)
		elif pattern == "ftp":
			if self.Config.props.ftp_enabled:
				OdsManager.create_server(self, pattern="ftp", require_pairing=True)
				
				
	def start_server(self, pattern):

		server = self.get_server(pattern)
		if server != None:
			if self.Config.props.shared_path == None:
				self.Config.props.shared_path = os.path.expanduser("~")
			
			if self.Config.props.shared_path == None:
				self.Config.props.shared_path = os.path.expanduser("~")
			
			if pattern == "opp":
				server.Start(self.Config.props.shared_path, True, False)
			elif pattern == "ftp":
				if self.Config.props.ftp_allow_write == None:
					self.Config.props.ftp_allow_write = False
			
				server.Start(self.Config.props.shared_path, self.Config.props.ftp_allow_write, True)
			return True
		else:
			return False
		
	def on_server_created(self, inst, server, pattern):
		def on_started(server):
			dprint(pattern, "Started")
			
		def on_session_created(server, session):
			self.transfers[session.object_path] = {}
			self.transfers[session.object_path]["notification"] = None
			self.transfers[session.object_path]["silent_transfers"] = 0
			
			dprint(pattern, "session created")
			if pattern != "opp":
				return
			
			def on_transfer_started(session, filename, local_path, total_bytes):
				dprint("transfer started", filename)
				info = server.GetServerSessionInfo(session.object_path)
				trusted = False
				try:
					dev = self.Applet.Manager.GetAdapter().FindDevice(info["BluetoothAddress"])
					dev = Device(dev)
					name = dev.Alias
					trusted = dev.Trusted
				except Exception, e:
					dprint(e)
					name = info["BluetoothAddress"]
			
			
				icon = get_icon("blueman", 48)

				self.transfers[session.object_path]["filename"] = filename
				self.transfers[session.object_path]["filepath"] = local_path
				self.transfers[session.object_path]["total"] = total_bytes
				self.transfers[session.object_path]["finished"] = False
				self.transfers[session.object_path]["failed"] = False
				self.transfers[session.object_path]["waiting"] = True
				
				self.transfers[session.object_path]["address"] = info["BluetoothAddress"]
				self.transfers[session.object_path]["name"] = name
				
				self.transfers[session.object_path]["transferred"] = 0
				
				if info["BluetoothAddress"] not in self.allowed_devices or (self.Config.props.opp_accept and not trusted):
					
					n = Notification(_("Incoming file"), 
					_("Incoming file %(0)s from %(1)s") % {"0":"<b>"+os.path.basename(filename)+"</b>", "1":"<b>"+name+"</b>"},
							30000, [["accept", _("Accept"), "gtk-yes"],["reject", _("Reject"), "gtk-no"]], access_cb, icon, self.Applet.status_icon)
				else:
					if total_bytes > 350000:
						n = Notification(_("Receiving file"), _("Receiving file %(0)s from %(1)s") % {"0":os.path.basename(filename), "1":name},
								pixbuf=icon, status_icon=self.Applet.status_icon)

					else:
						self.transfers[session.object_path]["silent_transfers"] += 1
						n = None
					
					access_cb(n, "accept")
				
				self.transfers[session.object_path]["notification"] = n
			
			def on_cancel(n, action):
				session.Cancel()
				dprint("cancel")
				
			def access_cb(n, action):
				t = self.transfers[session.object_path]
				dprint(action)
				
				if action == "closed":
					if t["waiting"]:
						session.Reject()					
				
				if t["waiting"]:
					if action == "accept":
						session.Accept()
						self.allowed_devices.append(t["address"])
						gobject.timeout_add(50000, self.allowed_devices.remove, t["address"])
					else:
						session.Reject()
					t["waiting"] = False

			def transfer_progress(session, bytes_transferred):
				self.transfers[session.object_path]["transferred"] = bytes_transferred
				
			def transfer_finished(session, type):
				dprint("---", type)
				if not self.transfers[session.object_path]["finished"]:
					t = self.transfers[session.object_path]
					if type != "cancelled" and type != "error":
						t["finished"] = True

						if t["total"] > 350000:	
							icon = get_icon("blueman", 48)
							self.transfers[session.object_path]["notification"] = Notification(_("File received"), 
									     _("File %(0)s from %(1)s successfully received") % {"0":t["filename"], "1":t["name"]},
									      pixbuf=icon, status_icon=self.Applet.status_icon)
						
					else:
						t["failed"] = True
						t["finished"] = True
						if t["notification"]:
							t["notification"].close()					
						t = self.transfers[session.object_path]
						icon = get_icon("blueman", 48)

						self.transfers[session.object_path]["notification"] = Notification(_("Transfer failed"), 
								_("Transfer of file %(0)s failed") % {"0":t["filename"], "1":t["name"]},
								 pixbuf=icon, status_icon=self.Applet.status_icon)
						
				if type == "disconnected":
					if self.transfers[session.object_path]["silent_transfers"] > 0:
						icon = get_icon("blueman", 48)
						Notification(_("Files received"), 
							     _("Received %d more files in the background") % self.transfers[session.object_path]["silent_transfers"],
							     pixbuf=icon, status_icon=self.Applet.status_icon)
					
					del self.transfers[session.object_path]
					
				
			session.GHandle("transfer-progress", transfer_progress)
			session.GHandle("cancelled", transfer_finished, "cancelled")
			session.GHandle("disconnected", transfer_finished, "disconnected")
			session.GHandle("transfer-completed", transfer_finished, "completed")
			session.GHandle("error-occurred", transfer_finished, "error")
			
			session.GHandle("transfer-started", on_transfer_started)
		
		server.GHandle("started", on_started)
		server.GHandle("session-created", on_session_created)
		
		
		self.start_server(pattern)
		
	def on_server_destroyed(self, inst, server):
		pass
