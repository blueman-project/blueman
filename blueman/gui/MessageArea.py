# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
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
import pango
from blueman.gui.GtkAnimation import WidgetFade
from blueman.Functions import get_icon

class MessageArea(gtk.EventBox):
	_inst_ = None
	
	def __new__(cls):
		if not MessageArea._inst_:
			MessageArea._inst_ = super(MessageArea, cls).__new__(cls)
		
		return MessageArea._inst_

	def __init__(self):
		gtk.EventBox.__init__(self)
		
		self.hbox = gtk.HBox()
		self.hbox.show()
		
		self.text = ""
		
		self.set_app_paintable(True)
			
		self.anim = WidgetFade(self.hbox, self.hbox.style.base[0])
		self.hl_anim = WidgetFade(self.hbox, gtk.gdk.Color(65535,0,0))
		
		self.setting_style = False
		
		self.hbox.props.spacing = 4
		self.hbox.set_border_width(2)
		
		self.icon = gtk.Image()
		self.icon.props.xpad = 4
		self.label = gtk.Label()
		self.label.props.xalign = 0
		self.label.set_ellipsize(pango.ELLIPSIZE_END)
		self.label.set_single_line_mode(True)
		self.label.set_selectable(True)
		
		
		self.b_more = gtk.Button(_("More"))
		im = gtk.Image()
		im.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_MENU)
		im.show()
		self.b_more.set_image(im)		
		self.b_more.props.relief = gtk.RELIEF_NONE
		
		im = gtk.Image()
		im.set_from_stock(gtk.STOCK_CANCEL, gtk.ICON_SIZE_MENU)
		im.show()
		self.b_close = gtk.Button()
		self.b_close.add(im)
		self.b_close.props.relief = gtk.RELIEF_NONE
		self.b_close.props.tooltip_text = _("Close")
		
		self.hbox.pack_start(self.icon, False,)
		self.hbox.pack_start(self.label, True)
		self.hbox.pack_start(self.b_more, False)
		self.hbox.pack_start(self.b_close, False)
		
		self.add(self.hbox)
		
		self.icon.show()
		self.b_close.show()
		self.label.show()
		self.b_more.show()
		
		self.b_close.connect("clicked", self.on_close)
		self.b_more.connect("clicked", self.on_more)

		
		self.hbox.connect("expose-event", self.expose_event)
		self.b_close.connect("style-set", self.style_set)
		
	def on_more(self, button):
		d = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_CLOSE)
		
		d.props.text = self.text
		
		d.run()
		d.destroy()
		
	def style_set(self, widget, prev_style):
		if self.setting_style:
			return
		
		#This is a hack needed to use the tooltip background color
		window = gtk.Window(gtk.WINDOW_POPUP)
		window.set_name("gtk-tooltip")
		window.ensure_style()
		style = window.get_style()
		window.destroy()
		
		self.setting_style = True
		
		#recursively set style
		def _set_style(wg):
			if isinstance(wg, gtk.Container):
				for w in wg:
					if not isinstance(w, gtk.Button):
						_set_style(w)

			wg.set_style(style)
		
		_set_style(self)
		self.anim.color = self.hbox.style.base[0]
		self.queue_draw()
		
		self.setting_style = False
		
		
	def on_close(self, button):
		def on_finished(anim):
			anim.disconnect(sig)
			self.props.visible = False
			anim.freeze()
		
		sig = self.anim.connect("animation-finished", on_finished)
		self.anim.thaw()
		self.anim.animate(start=1.0, end=0.0, duration=500)

	@staticmethod
	def close():
		MessageArea._inst_.on_close(None)
	
	@staticmethod
	def show_message(*args):
		MessageArea._inst_._show_message(*args)
	
	def _show_message(self, text, icon=gtk.STOCK_DIALOG_WARNING):
		self.text = text
		
		self.label.set_tooltip_text(text)
		self.icon.set_from_stock(icon, gtk.ICON_SIZE_MENU)
		
		if icon == gtk.STOCK_DIALOG_WARNING:
			self.hl_anim.color = gtk.gdk.Color(65535,0,0)
		else:
			self.hl_anim.color = gtk.gdk.Color(0,0,65535)
		
		def on_finished(anim):
			anim.disconnect(sig)
			anim.freeze()		
		
		if not self.props.visible:
			sig = self.anim.connect("animation-finished", on_finished)
			
			self.anim.thaw()
			
			self.show()
			self.anim.animate(start=0.0, end=1.0, duration=500)
		else:
			sig = self.hl_anim.connect("animation-finished", on_finished)
			self.hl_anim.thaw()
			self.hl_anim.animate(start=0.7, end=1.0, duration=1000)
		
		lines = text.split("\n")
		if len(lines) > 1:
			self.label.props.label = lines[0] + "..."
			self.b_more.props.visible = True
		else:
			self.label.props.label = text
			self.b_more.props.visible = False
		
	def expose_event(self, window, event):
		window.style.paint_box(window.window,
			gtk.STATE_NORMAL, gtk.SHADOW_IN,
			None, window, "tooltip",
			window.allocation.x, window.allocation.y, window.allocation.width, window.allocation.height)		

		return False

