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
import os.path

class Transfer(OdsManager):

	def __init__(self):
		OdsManager.__init__(self)
		
		self.GHandle("server-created", self.on_server_created)
		
		#check options
		self.create_server()
		
		self.Config = Config("transfer")
		
		
	def on_server_created(self, inst, server):
		def on_started(server):
			print "Started"
			
		def on_session_created(server, session):
			print "session created"
			def on_transfer_started(session, filename, local_path, total_bytes):
				def transfer_progress(session, bytes_transferred):
					print "progress", bytes_transferred
					
				def transfer_finished(session):
					print "finished"
					
				session.GHandle("transfer-progress", transfer_progress)
				session.GHandle("cancelled", transfer_finished)
				session.GHandle("disconnected", transfer_finished)
				session.GHandle("transfer-completed", transfer_finished)
				session.GHandle("error-occured", transfer_finished)
				
			session.GHandle("transfer-started", on_transfer_started)
		
		server.GHandle("started", on_started)
		server.GHandle("session-created", on_session_created)
		
		
		if self.Config.props.opp_shared_path == None:
			self.Config.props.opp_shared_path = os.path.expanduser("~")
		
		server.Start(self.Config.props.opp_shared_path, True, True)
		
	def on_server_destroyed(self, inst, server):
		pass
