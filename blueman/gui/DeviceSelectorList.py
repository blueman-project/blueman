# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango
from html import escape
from blueman.Functions import *
from blueman.gui.DeviceList import DeviceList


class DeviceSelectorList(DeviceList):
    def __init__(self, adapter=None):
        cr = Gtk.CellRendererText()
        cr.props.ellipsize = Pango.EllipsizeMode.END
        data = [
            #device picture
            ["found_pb", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 0}, None,
             {"spacing": 0, "sizing": Gtk.TreeViewColumnSizing.AUTOSIZE}],
            ["device_pb", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 1}, None],

            #device caption
            ["caption", str, cr, {"markup": 2}, None, {"expand": True}],

            ["bonded_icon", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 3}, None],
            ["trusted_icon", GdkPixbuf.Pixbuf, Gtk.CellRendererPixbuf(), {"pixbuf": 4}, None]

            #["connected", bool], #used for quick access instead of device.GetProperties
            #["bonded", bool], #used for quick access instead of device.GetProperties
            #["trusted", bool], #used for quick access instead of device.GetProperties
        ]

        super(DeviceSelectorList, self).__init__(adapter, data)
        self.props.headers_visible = False

    def row_setup_event(self, tree_iter, device):
        self.row_update_event(tree_iter, "Trusted", device['Trusted'])
        self.row_update_event(tree_iter, "Paired", device['Paired'])
        self.row_update_event(tree_iter, "Alias", device['Alias'])
        self.row_update_event(tree_iter, "Icon", device['Icon'])

    def row_update_event(self, tree_iter, key, value):
        if key == "Trusted":
            if value:
                self.set(tree_iter, trusted_icon=get_icon("blueman-trust", 16))
            else:
                self.set(tree_iter, trusted_icon=None)

        elif key == "Paired":
            if value:
                self.set(tree_iter, bonded_icon=get_icon("dialog-password", 16))
            else:
                self.set(tree_iter, bonded_icon=None)

        elif key == "Alias":
            self.set(tree_iter, caption=escape(value))

        elif key == "Icon":
            self.set(tree_iter, device_pb=get_icon(value, 16))
