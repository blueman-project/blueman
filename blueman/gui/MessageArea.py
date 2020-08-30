from gettext import gettext as _
from typing import Optional

from blueman.gui.GtkAnimation import WidgetFade

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import Pango


class MessageArea(Gtk.InfoBar):
    _inst_: "MessageArea"

    def __new__(cls) -> "MessageArea":
        if not hasattr(MessageArea, "_inst_"):
            MessageArea._inst_ = super().__new__(cls)

        return MessageArea._inst_

    def __init__(self) -> None:
        super().__init__(show_close_button=True)

        self.set_name("MessageArea")

        self.text = ""

        self.anim = WidgetFade(self, self.get_style_context().get_background_color(Gtk.StateFlags.NORMAL))
        self.hl_anim = WidgetFade(self, Gdk.RGBA(1, 0, 0, 1))

        self.icon = Gtk.Image(pixel_size=16, visible=True)
        self.label = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, single_line_mode=True,
                               selectable=True, visible=True)

        im = Gtk.Image(icon_name="dialog-information", pixel_size=16, visible=True)
        self.b_more = self.add_button(_("More"), 0)
        self.b_more.set_image(im)
        self.b_more.props.relief = Gtk.ReliefStyle.NONE

        self.content_area = self.get_content_area()
        self.content_area.add(self.icon)
        self.content_area.add(self.label)

        self.connect("response", self.on_response)

    def on_response(self, info_bar: Gtk.InfoBar, response_id: int) -> None:
        if response_id == 0:
            assert self.bt is not None
            parent = self.get_toplevel()
            assert isinstance(parent, Gtk.Container)
            d = Gtk.MessageDialog(parent=parent, type=Gtk.MessageType.INFO,
                                  buttons=Gtk.ButtonsType.CLOSE, text='\n'.join((self.text, self.bt)))
            d.run()
            d.destroy()
        elif response_id == Gtk.ResponseType.CLOSE:
            info_bar.props.visible = False

    @staticmethod
    def close() -> None:
        MessageArea._inst_.response(1)

    @staticmethod
    def show_message(text: str, bt: Optional[str] = None, icon: str = "dialog-warning") -> None:
        MessageArea._inst_._show_message(text, bt, icon)

    def _show_message(self, text: str, bt: Optional[str] = None, icon: str = "dialog-warning") -> None:
        def on_finished(anim: WidgetFade) -> None:
            anim.disconnect(sig)
            anim.freeze()

        self.text = text
        self.bt = bt

        self.label.props.tooltip_text = text
        self.icon.props.icon_name = icon

        if icon == "dialog-warning":
            self.set_message_type(Gtk.MessageType.ERROR)
            self.hl_anim.color = Gdk.RGBA(1, 0, 0, 1)
        else:
            self.set_message_type(Gtk.MessageType.INFO)
            self.hl_anim.color = Gdk.RGBA(0, 0, 1, 1)

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
            self.label.props.label = self.text + "…"
            self.b_more.props.visible = True
        else:
            self.label.props.label = self.text
            self.b_more.props.visible = False

        # Queue a resize to workaround negative height problem, see issue #369
        # TODO revisit this in later Gtk versions to see if the problem persists
        self.queue_resize()
