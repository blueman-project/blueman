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

import pynotify
import gtk
from blueman.Functions import dprint
from blueman.gui.GtkAnimation import AnimBase, BezierController

pynotify.init("blueman")

OPACITY_START = 0.7

class Fade(AnimBase):
	def __init__(self, window):
		AnimBase.__init__(self, state=OPACITY_START)
		self.window = window
		
	def state_changed(self, state):
		self.window.props.opacity = state

class NotificationDialog(gtk.MessageDialog):
	def __init__(self, summary, message, timeout=-1, actions=None, actions_cb=None, pixbuf=None, status_icon=None):
		gtk.MessageDialog.__init__(self, parent=None, flags=0, type=gtk.MESSAGE_QUESTION, buttons=gtk.BUTTONS_NONE, message_format=None)
		
		self.bubble = NotificationBubble(summary, message, pixbuf=pixbuf)
		
		i = 100
		self.actions = {}
		self.callback = actions_cb
		if actions:
			for a in actions:
				action_id = a[0]
				action_name = a[1]
				if len(a) == 3:
					icon_name = a[2]
				else:
					icon_name = None
				
				self.actions[i] = action_id
				button = self.add_button(action_name, i)
				if icon_name:
					im = gtk.image_new_from_icon_name(icon_name, gtk.ICON_SIZE_BUTTON)
					im.show()
					button.props.image = im
				i += 1
				
		self.actions[gtk.RESPONSE_DELETE_EVENT] = "close"
		
		self.props.secondary_use_markup = True
		self.resize(350, 50)
		
		self.fader = Fade(self)

		self.props.skip_taskbar_hint = False
		
		self.props.title = summary
		self.props.text = summary
		self.props.secondary_text = message
		
		self.props.window_position = gtk.WIN_POS_CENTER

		if pixbuf:
			self.set_icon_from_pixbuf(pixbuf)
		
		self.connect("response", self.dialog_response)
		self.props.icon_name = "blueman"		
		
		self.entered = False
		def on_enter(widget, event):
			if self.window == gtk.gdk.window_at_pointer()[0] or not self.entered:
				self.fader.animate(start=self.fader.get_state(), end=1.0, duration=500)
				self.entered = True
		
		def on_leave(widget, event):
			if not gtk.gdk.window_at_pointer():
				self.entered = False
				self.fader.animate(start=self.fader.get_state(), end=OPACITY_START, duration=500)
		
		self.connect("enter-notify-event", on_enter)
		self.connect("leave-notify-event", on_leave)

		
		self.set_opacity(OPACITY_START)
		self.present()
		self.set_opacity(OPACITY_START)

		
	def get_id(self):
		if self.bubble:
			return self.bubble.props.id
		
	def dialog_response(self, dialog, response):
		if self.callback:
			self.callback(self, self.actions[response])
		self.hide()
		
	def close(self):
		self.hide()
		
	def set_hint(*args):
		dprint("stub")
		
	def set_timeout(*args):
		dprint("stub")
		
	def add_action(*args):
		dprint("stub")
		
	def clear_actions(*args):
		dprint("stub")
		
	def set_urgency(*args):
		dprint("stub")
		
	def update(self, summary, message):
		self.props.title = summary
		
		self.props.text = summary
		self.props.secondary_text = message
		self.present()
		
	def set_icon_from_pixbuf(self, pixbuf):
		im = gtk.image_new_from_pixbuf(pixbuf)
		self.set_image(im)
		im.show()
	

class NotificationBubble(pynotify.Notification):
	def __init__(self, summary, message, timeout=-1, actions= None, actions_cb=None, pixbuf=None, status_icon=None):
		pynotify.Notification.__init__(self, summary, message)

		def on_notification_closed(n, *args):
			self.disconnect(closed_sig)
			if actions_cb:
				actions_cb(n, "closed")
		
		def on_action(*args):
			self.disconnect(closed_sig)
			actions_cb(*args)	
		
		if pixbuf:
			self.set_icon_from_pixbuf(pixbuf)
		
		if actions:
			for action in actions:
				self.add_action(action[0], action[1], on_action)
			self.add_action("default", "Default Action", on_action)
		
		closed_sig = self.connect("closed", on_notification_closed)
		if timeout != -1:
			self.set_timeout(timeout)
		if status_icon:
			screen, area, orientation = status_icon.get_geometry()
			self.set_hint("x", area.x + area.width/2)
			self.set_hint("y", area.y + area.height/2)
		
		self.show()	
		
	def get_id(self):
		return self.props.id
	

class Notification(object):
	@staticmethod
	def actions_supported():
		return "actions" in pynotify.get_server_caps()
	
	def __new__(cls, summary, message, timeout=-1, actions= None, actions_cb=None, pixbuf=None, status_icon=None):
		if not "actions" in pynotify.get_server_caps():
			if actions != None:
				return NotificationDialog(summary, message, timeout, actions, actions_cb, pixbuf, status_icon)
				
		return NotificationBubble(summary, message, timeout, actions, actions_cb, pixbuf, status_icon)


