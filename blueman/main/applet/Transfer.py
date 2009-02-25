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
					dev.Destroy()
				except Exception, e:
					dprint(e)
					name = info["BluetoothAddress"]
			
			
				icon = composite_icon(get_icon("blueman-send-file", 48), [(get_icon("blueman", 24), 24, 24, 255)])
				n = pynotify.Notification(_("Incoming File"), _("Incoming file %(0)s from %(1)s") % {"0":os.path.basename(filename), "1":name})
				n.set_icon_from_pixbuf(icon)
				n.set_timeout(30000)
				n.set_category("bluetooth.transfer")
				n.attach_to_status_icon(self.Applet.status_icon)
				n.add_action("accept", _("Accept"), access_cb)
				n.add_action("reject", _("Reject"), access_cb)
				n.add_action("default", "Default Action", access_cb)
			
				closed_sig = n.connect("closed", on_closed)
			
				self.transfers[session.object_path]["notification"] = n
				self.transfers[session.object_path]["filename"] = filename
				self.transfers[session.object_path]["filepath"] = local_path
				self.transfers[session.object_path]["total"] = total_bytes
				self.transfers[session.object_path]["finished"] = False
				self.transfers[session.object_path]["failed"] = False
				self.transfers[session.object_path]["waiting"] = True
				self.transfers[session.object_path]["calc"] = SpeedCalc()
				self.transfers[session.object_path]["updater"] = gobject.timeout_add(1000, update_notification, n)
				self.transfers[session.object_path]["transferred"] = 0
				self.transfers[session.object_path]["closed_sig"] = closed_sig
				if not self.Config.props.opp_accept or not trusted:
					n.show()
				else:
					access_cb(n, "accept")
			
			def on_cancel(n, action):
				session.Cancel()
				dprint("cancel")
				
			def access_cb(n, action):
				t = self.transfers[session.object_path]
				dprint(action)
				if t["waiting"]:
					if action == "accept":
						session.Accept()
					else:
						session.Reject()
					
					if not t["notification"] == None:
						t["waiting"] = False
						if action == "reject" or action == "default":
							n.close()
						else:
							dprint("clearing actions")
							n.clear_actions()
							n.add_action("cancel", _("Cancel"), on_cancel)
							n.set_urgency(pynotify.URGENCY_NORMAL)
							n.set_timeout(0)
							update_notification(n)
				
			def on_closed(n):
				dprint("closed")
				t = self.transfers[session.object_path]
				if t["waiting"]:
					session.Reject()
				
				if not self.transfers[session.object_path]["finished"]:
					gobject.source_remove(self.transfers[session.object_path]["updater"])
					self.transfers[session.object_path]["notification"] = None


			def show_open():
				dprint("open")
				path = self.transfers[session.object_path]["filepath"]
				name = self.transfers[session.object_path]["filename"]
				
				def on_open(n, action):
					dprint(action)
					if action == "open":
						try:
							spawn(["xdg-open", path], True)
						except Exception, e:
							dprint(e)
				
				n = self.Applet.show_notification(_("File Saved"), _("Would you like to open %s?") % name, timeout=0, 
									actions=[["open", _("Open")]], 
									actions_cb=on_open, pixbuf=get_icon("gtk-save", 48))
					
			def update_notification(n):
				t = self.transfers[session.object_path]
				dprint(t["finished"])
				if not t["waiting"]:
					if t["finished"]:
						#print t["transferred"], t["total"]
						#if t["transferred"] == t["total"]:
						if n:
							n.disconnect(self.transfers[session.object_path]["closed_sig"])
							n.close()

						if not t["failed"]:
							gobject.idle_add(show_open)
						
						return False
					
					else:
						
						spd = format_bytes(t["calc"].calc(t["transferred"]))
						trans = format_bytes(t["transferred"])
						tot = format_bytes(t["total"])
	
						n.update(_("Receiving File"), _("Receiving File %(0)s\n%(1).2f%(2)s out of %(3).2f%(4)s (%(5).2f%(6)s/s)") % {"0":t["filename"],"1":trans[0], "2":trans[1], "3":tot[0], "4":tot[1], "5":spd[0], "6":spd[1]})
						n.show()
				
				return True
					
			

			
			def transfer_progress(session, bytes_transferred):
				#print "progress", bytes_transferred
				self.transfers[session.object_path]["transferred"] = bytes_transferred
				
			def transfer_finished(session, type):
				dprint("---", type)
				#try:
				if not self.transfers[session.object_path]["finished"]:
					if type != "cancelled" and type != "error":
						self.transfers[session.object_path]["finished"] = True
						update_notification(self.transfers[session.object_path]["notification"])
					else:
						self.transfers[session.object_path]["failed"] = True
						self.transfers[session.object_path]["finished"] = True
						
				if type == "disconnected":
					del self.transfers[session.object_path]
					
				if type == "completed":
					gobject.source_remove(self.transfers[session.object_path]["updater"])
					
				#except KeyError:
				#	pass
					
				
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
