# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class NetworkErrorDialog(Gtk.MessageDialog):
    def __init__(self, excp, secondary_markup=None, parent=None):
        super(NetworkErrorDialog, self).__init__(parent=parent,
            buttons=Gtk.ButtonsType.OK, type=Gtk.MessageType.ERROR)

        self.set_name("NetworkErrorDialog")
        self.props.icon_name = "dialog.error"
        self.set_markup("<b>Failed to apply network settings</b>")

        if secondary_markup:
            self.format_secondary_markup(secondary_markup)

        self.message_box = self.get_message_area()

        label_expander = Gtk.Label()
        label_expander.set_markup("<b>Exception</b>")

        excp_label = Gtk.Label(str(excp))
        excp_label.props.selectable = True

        self.expander = Gtk.Expander()
        self.expander.set_label_widget(label_expander)
        self.expander.add(excp_label)

        self.message_box.pack_start(self.expander, False, False, 10)
        self.message_box.show_all()
