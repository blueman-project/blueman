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
from blueman.main.Config import Config
from blueman.ods.OdsManager import OdsManager
from blueman.main.Device import Device
from blueman.Functions import *
import os.path
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
		
		#check options
		self.create_server()
		
		self.Config = Config("transfer")
	def access_cb(self, n, action):
		print "cb", action
		
		if action == "accept":
			session.Accept()
		else:
			session.Reject()
		
	def on_server_created(self, inst, server):
		def on_started(server):
			print "Started"
			
		def on_session_created(server, session):
			print "session created"
			def on_transfer_started(session, filename, local_path, total_bytes):
				def on_cancel(n, action):
					session.Cancel()
					print "cancel"
				
				def access_cb(n, action):
					t = self.transfers[session.object_path]
					
					if t["waiting"]:
						if action == "accept":
							session.Accept()
						else:
							session.Reject()
						
						if not t["notification"] == None:
							t["waiting"] = False
							print "clearing actions"
							n.clear_actions()
							n.add_action("cancel", _("Cancel"), on_cancel)
							update_notification(n)
					
				def on_closed(n):
					t = self.transfers[session.object_path]
					if t["waiting"]:
						session.Reject()
					
					if not self.transfers[session.object_path]["finished"]:
						gobject.source_remove(self.transfers[session.object_path]["updater"])
						self.transfers[session.object_path]["notification"] = None
					
						


						

						
				def update_notification(n):
					t = self.transfers[session.object_path]

					if not t["waiting"]:
						if t["finished"]:
							print "show final"
							n.disconnect(closed_sig)
							
							gobject.source_remove(self.transfers[session.object_path]["updater"])
							
							del self.transfers[session.object_path]
							
							n.close()
							
							return False
						
						else:
						
							n.update("a", "Receiving File %s (%s)" % (os.path.basename(self.transfers[session.object_path]["filename"]), self.transfers[session.object_path]["transferred"]))
							n.show()
					
					return True
						
				
				info = server.GetServerSessionInfo(session.object_path)

				try:
					dev = self.Applet.Manager.FindDevice(info["BluetoothAddress"])
					dev = Device(dev)
					name = dev.Alias
					dev.Destroy()
				except:
					name = info["BluetoothAddress"]
				
				icon = composite_icon(get_icon("blueman-send-file", 48), [(get_icon("blueman", 24), 24, 24, 255)])
				n = pynotify.Notification(_("Incoming File"), _("Incoming file %s from %s") % (os.path.basename(filename), name))
				n.set_icon_from_pixbuf(icon)
				n.set_category("bluetooth.transfer")
				n.attach_to_status_icon(self.Applet.status_icon)
				n.add_action("accept", _("Accept"), access_cb)
				n.add_action("reject", _("Reject"), access_cb)
				n.add_action("default", "Default Action", access_cb)
				n.show()
				closed_sig = n.connect("closed", on_closed)
				
				self.transfers[session.object_path] = {}
				self.transfers[session.object_path]["notification"] = n
				self.transfers[session.object_path]["filename"] = filename
				self.transfers[session.object_path]["total"] = total_bytes
				self.transfers[session.object_path]["finished"] = False
				self.transfers[session.object_path]["waiting"] = True
				self.transfers[session.object_path]["updater"] = gobject.timeout_add(1000, update_notification, n)
				
				def transfer_progress(session, bytes_transferred):
					#print "progress", bytes_transferred
					self.transfers[session.object_path]["transferred"] = bytes_transferred
					
				def transfer_finished(session, type):
					print "---", type
					try:
						if not self.transfers[session.object_path]["finished"]:
							self.transfers[session.object_path]["finished"] = True
							update_notification(n)
					except KeyError:
						pass
						
					
				session.GHandle("transfer-progress", transfer_progress)
				session.GHandle("cancelled", transfer_finished, "cancelled")
				session.GHandle("disconnected", transfer_finished, "disconnected")
				session.GHandle("transfer-completed", transfer_finished, "completed")
				session.GHandle("error-occured", transfer_finished, "error")
				
			session.GHandle("transfer-started", on_transfer_started)
		
		server.GHandle("started", on_started)
		server.GHandle("session-created", on_session_created)
		
		
		if self.Config.props.opp_shared_path == None:
			self.Config.props.opp_shared_path = os.path.expanduser("~")
		
		server.Start(self.Config.props.opp_shared_path, True, False)
		
	def on_server_destroyed(self, inst, server):
		pass
