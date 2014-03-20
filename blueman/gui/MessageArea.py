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

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from gi.repository import GObject
from blueman.gui.GtkAnimation import WidgetFade
from blueman.Constants import *
from blueman.Functions import get_icon

class MessageArea(Gtk.EventBox):
	_inst_ = None
	
	def __new__(cls):
		if not MessageArea._inst_:
			MessageArea._inst_ = super(MessageArea, cls).__new__(cls)
		
		return MessageArea._inst_

	def __init__(self):
		GObject.GObject.__init__(self)
		
		self.hbox = Gtk.HBox()
		self.hbox.show()
		
		self.text = ""
		
		self.set_app_paintable(True)
		
		self.anim = WidgetFade(self.hbox, self.hbox.get_style().lookup_color("base_color")[1])
		self.hl_anim = WidgetFade(self.hbox, Gdk.Color(65535,0,0))
		
		self.setting_style = False
		
		self.hbox.props.spacing = 4
		self.hbox.set_border_width(2)
		
		self.icon = Gtk.Image()
		self.icon.props.xpad = 4
		self.label = Gtk.Label()
		self.label.props.xalign = 0
		self.label.set_ellipsize(Pango.EllipsizeMode.END)
		self.label.set_single_line_mode(True)
		self.label.set_selectable(True)
		
		
		self.b_more = Gtk.Button(_("More"))
		im = Gtk.Image()
		im.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.MENU)
		im.show()
		self.b_more.set_image(im)		
		self.b_more.props.relief = Gtk.ReliefStyle.NONE
		
		im = Gtk.Image()
		im.set_from_stock(Gtk.STOCK_CANCEL, Gtk.IconSize.MENU)
		im.show()
		self.b_close = Gtk.Button()
		self.b_close.add(im)
		self.b_close.props.relief = Gtk.ReliefStyle.NONE
		self.b_close.props.tooltip_text = _("Close")
		
		self.hbox.pack_start(self.icon, False, False, 0)
		self.hbox.pack_start(self.label, True, False, 0)
		self.hbox.pack_start(self.b_more, False, False, 0)
		self.hbox.pack_start(self.b_close, False, False, 0)
		
		self.add(self.hbox)
		
		self.icon.show()
		self.b_close.show()
		self.label.show()
		self.b_more.show()
		
		self.b_close.connect("clicked", self.on_close)
		self.b_more.connect("clicked", self.on_more)

		self.hbox.connect("draw", self.draw)
		self.b_close.connect("style-set", self.style_set)
		
	def on_more(self, button):
		d = Gtk.MessageDialog(parent=None, flags=0, type=Gtk.MessageType.INFO, buttons=Gtk.ButtonsType.CLOSE)
		
		d.props.text = self.text
		
		d.run()
		d.destroy()
		
	def style_set(self, widget, prev_style):
		if self.setting_style:
			return
		
		#This is a hack needed to use the tooltip background color
		window = Gtk.Window(Gtk.WindowType.POPUP)
		window.set_name("gtk-tooltip")
		window.ensure_style()
		style = window.get_style()
		window.destroy()
		
		self.setting_style = True
		
		#recursively set style
		def _set_style(wg):
			if isinstance(wg, Gtk.Container):
				for w in wg:
					if not isinstance(w, Gtk.Button):
						_set_style(w)

			wg.set_style(style)
		
		_set_style(self)
		self.anim.color = self.hbox.get_style_context().get_background_color(0)
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
	
	def _show_message(self, text, icon=Gtk.STOCK_DIALOG_WARNING):
		self.text = text
		
		self.label.set_tooltip_text(text)
		self.icon.set_from_stock(icon, Gtk.IconSize.MENU)
		
		if icon == Gtk.STOCK_DIALOG_WARNING:
			self.hl_anim.color = Gdk.Color(65535,0,0)
		else:
			self.hl_anim.color = Gdk.Color(0,0,65535)
		
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
		
	def draw(self, window, cr):
		rect = window.get_allocation()
		Gtk.paint_box(window.get_style(), cr,
			Gtk.StateType.NORMAL, Gtk.ShadowType.IN,
			window, "tooltip",
			rect.x, rect.y, rect.width, rect.height)
	def expose_event(self, window, event):
		rect = window.get_allocation()
		window.style.paint_box(window.window,
			Gtk.StateType.NORMAL, Gtk.ShadowType.IN,
			None, window, "tooltip",
			rect.x, rect.y, rect.width, rect.height)

		return False

