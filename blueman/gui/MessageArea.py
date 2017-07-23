# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango
from blueman.gui.GtkAnimation import WidgetFade


class MessageArea(Gtk.EventBox):
    _inst_ = None

    def __new__(cls):
        if not MessageArea._inst_:
            MessageArea._inst_ = super(MessageArea, cls).__new__(cls)

        return MessageArea._inst_

    def __init__(self):
        super(MessageArea, self).__init__()

        self.set_name("MessageArea")
        self.hbox = Gtk.Box(spacing=4, border_width=2, orientation=Gtk.Orientation.HORIZONTAL, visible=True)

        self.text = ""

        self.set_app_paintable(True)

        self.anim = WidgetFade(self.hbox, self.hbox.get_style_context().get_background_color(Gtk.StateFlags.NORMAL))
        self.hl_anim = WidgetFade(self.hbox, Gdk.RGBA(1, 0, 0, 1))

        self.setting_style = False

        self.icon = Gtk.Image(pixel_size=16, visible=True)
        self.label = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, single_line_mode=True,
                               selectable=True, visible=True)

        im = Gtk.Image(icon_name="dialog-information", pixel_size=16, visible=True)
        self.b_more = Gtk.Button(label=_("More"), relief=Gtk.ReliefStyle.NONE, visible=True, image=im)

        im = Gtk.Image(icon_name="window-close", pixel_size=16, visible=True)
        self.b_close = Gtk.Button(label=_("Close"), relief=Gtk.ReliefStyle.NONE, tooltip_text=_("Close"),
                                  visible=True, image=im)

        self.hbox.pack_start(self.icon, False, False, 4)
        self.hbox.pack_start(self.label, True, False, 0)
        self.hbox.pack_start(self.b_more, False, False, 0)
        self.hbox.pack_start(self.b_close, False, False, 0)

        self.add(self.hbox)

        self.b_close.connect("clicked", self.on_close)
        self.b_more.connect("clicked", self.on_more)

        self.hbox.connect("draw", self.draw)
        self.b_close.connect("style-set", self.style_set)

    def on_more(self, button):
        d = Gtk.MessageDialog(parent=self.get_toplevel(), flags=0, type=Gtk.MessageType.INFO,
                              buttons=Gtk.ButtonsType.CLOSE, text='\n'.join((self.text, self.bt)))
        d.run()
        d.destroy()

    def style_set(self, widget, prev_style):
        # FIXME needs porting to GtkStyleContext
        if self.setting_style:
            return

        # This is a hack needed to use the tooltip background color
        window = Gtk.Window(type=Gtk.WindowType.POPUP, name="gtk-tooltip")
        window.ensure_style()
        style = window.get_style()
        window.destroy()

        self.setting_style = True

        # recursively set style
        def _set_style(wg):
            if isinstance(wg, Gtk.Container):
                for w in wg:
                    if not isinstance(w, Gtk.Button):
                        _set_style(w)

            wg.set_style(style)

        _set_style(self)
        self.anim.color = self.hbox.get_style_context().get_background_color(Gtk.StateFlags.NORMAL)
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

    def _show_message(self, text, bt=None, icon="dialog-warning"):
        self.text = text
        self.bt = bt

        self.label.props.tooltip_text = text
        self.icon.props.icon_name = icon

        if icon == "dialog-warning":
            self.hl_anim.color = Gdk.RGBA(1, 0, 0, 1)
        else:
            self.hl_anim.color = Gdk.RGBA(0, 0, 1, 1)

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

        if self.bt:
            self.label.props.label = self.text + "..."
            self.b_more.props.visible = True
        else:
            self.label.props.label = self.text
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

