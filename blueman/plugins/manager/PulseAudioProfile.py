# Copyright (C) 2010 Valmantas Paliksa <walmis at balticum-tv dot lt>
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

from blueman.plugins.ManagerPlugin import ManagerPlugin
from blueman.main.PulseAudioUtils import PulseAudioUtils, EventType
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.gui.MessageArea import MessageArea
from blueman.Functions import get_icon, create_menuitem

import gtk

class PulseAudioProfile(ManagerPlugin):

	def on_load(self, user_data):
		self.devices = {}
		self.item = None
		
		self.deferred = []
		
		pa = PulseAudioUtils()
		pa.connect("event", self.on_pa_event)
		pa.connect("connected", self.on_pa_ready)
		
	def on_pa_ready(self, utils):
		dprint("connected")
		for dev in self.deferred:
			self.regenerate_with_device(dev.Address)
			
		self.deferred = []
		
		
	#updates all menu instances with the following device address
	def regenerate_with_device(self, device_addr):
		for inst in ManagerDeviceMenu.__instances__:
			if inst.SelectedDevice.Address == device_addr and not inst.is_popup:
				inst.Generate()
		
	def on_pa_event(self, utils, event, idx):
		dprint(event, idx)
		
		def get_card_cb(card):
			if card["driver"] == "module-bluetooth-device.c":
				self.devices[card["proplist"]["device.string"]] = card
				self.regenerate_with_device(card["proplist"]["device.string"])
		
		if event & EventType.CARD:
			print "card",
			if event & EventType.CHANGE:
				print "change"
				utils.GetCard(idx, get_card_cb)
			elif event & EventType.REMOVE:
				print "remove"
			else:
				print "add"
				utils.GetCard(idx, get_card_cb)
		
		
	def is_connected(self, device):
		try:
			s = device.Services["audiosink"]
			props = s.GetProperties()
			if props["Connected"]:
				return True
		except KeyError:
			pass
		
		try:
			s = device.Services["audiosource"]
			props = s.GetProperties()
			if props["State"] != "disconnected":
				return True			
		except KeyError:
			pass		
		
		try:
			s = device.Services["headset"]
			props = s.GetProperties()
			if props["State"] != "disconnected":
				return True			
		except KeyError:
			pass
			
		return False
		
	def query_pa(self, device):
		def list_cb(cards):
			for c in cards.itervalues():
				if c["proplist"]["device.string"] == device.Address:
					self.devices[device.Address] = c
					self.generate_menu(device)
		
		pa = PulseAudioUtils()
		pa.ListCards(list_cb)
		
	def on_selection_changed(self, item, device, profile):
		if item.get_active():
			pa = PulseAudioUtils()
			
			c = self.devices[device.Address]
			
			def on_result(res):
				if not res:
					MessageArea.show_message(_("Failed to change profile to %s" % profile))
			
			pa.SetCardProfile(c["index"], profile, on_result)
		
	def generate_menu(self, device):
		info = self.devices[device.Address]
		items = []
		
		sub = gtk.Menu()
		
		if info:
			for profile in info["profiles"]:	
				i = gtk.RadioMenuItem(items[0] if len(items) else None, 
									  profile["description"])
									  
				if profile["name"] == info["active_profile"]:
					i.set_active(True)
				
				i.connect("toggled", self.on_selection_changed,
						  device, profile["name"])
									  
				items.append(i)
				sub.append(i)
				i.show()
				
			self.item.set_submenu(sub)
			self.item.show()
		
	def on_request_menu_items(self, manager_menu, device):
		
		if self.is_connected(device):
			pa = PulseAudioUtils()
			if not pa.connected:
				self.deferred.append(device)
				return
				
			self.item = create_menuitem(_("Audio Profile"), get_icon("audio-card", 16))
			self.item.props.tooltip_text = _("Select audio profile for PulseAudio")		
			
			if not device.Address in self.devices:
				self.query_pa(device)
			else:
				self.generate_menu(device)
		
		else:
			return
		
		return [(self.item, 300)]
