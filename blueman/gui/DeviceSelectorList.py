# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango
from html import escape
from blueman.gui.DeviceList import DeviceList


class DeviceSelectorList(DeviceList):
    def __init__(self, adapter=None):
        cr = Gtk.CellRendererText()
        cr.props.ellipsize = Pango.EllipsizeMode.END
        tabledata = [
            #device picture
            {"id": "device_pb", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 0}},
            #device caption
            {"id": "caption", "type": str, "renderer": cr, "render_attrs": {"markup": 1},
             "view_props": {"expand": True}},
            {"id": "paired_icon", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 2}},
            {"id": "trusted_icon", "type": GdkPixbuf.Pixbuf, "renderer": Gtk.CellRendererPixbuf(),
             "render_attrs": {"pixbuf": 3}}
        ]

        super(DeviceSelectorList, self).__init__(adapter, tabledata, headers_visible=False)

    def on_icon_theme_changed(self, widget):
        for row in self.liststore:
            device = self.get(row.iter, "device")["device"]
            self.row_setup_event(row.iter, device)

    def row_setup_event(self, tree_iter, device):
        self.row_update_event(tree_iter, "Trusted", device['Trusted'])
        self.row_update_event(tree_iter, "Paired", device['Paired'])
        self.row_update_event(tree_iter, "Alias", device['Alias'])
        self.row_update_event(tree_iter, "Icon", device['Icon'])

    def row_update_event(self, tree_iter, key, value):
        if key == "Trusted":
            if value:
                icon = self.icon_theme.load_icon("blueman-trust", 16, Gtk.IconLookupFlags.FORCE_SIZE)
                self.set(tree_iter, trusted_icon=icon)
            else:
                self.set(tree_iter, trusted_icon=None)

        elif key == "Paired":
            if value:
                icon = self.icon_theme.load_icon("dialog-password", 16, Gtk.IconLookupFlags.FORCE_SIZE)
                self.set(tree_iter, paired_icon=icon)
            else:
                self.set(tree_iter, paired_icon=None)

        elif key == "Alias":
            self.set(tree_iter, caption=escape(value))

        elif key == "Icon":
            icon = self.icon_theme.load_icon(value, 16, Gtk.IconLookupFlags.FORCE_SIZE)
            self.set(tree_iter, device_pb=icon)
