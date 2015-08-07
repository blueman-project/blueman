from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Pango
import cgi
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
            #["fake", bool], #used for quick access instead of device.GetProperties,
            #fake determines whether device is "discovered" or a real bluez device
        ]

        DeviceList.__init__(self, adapter, data)
        self.props.headers_visible = False

    def row_setup_event(self, iter, device):
        if not device.Fake:
            self.row_update_event(iter, "Trusted", device.Trusted)
            self.row_update_event(iter, "Paired", device.Paired)
        self.row_update_event(iter, "Fake", device.Fake)
        self.row_update_event(iter, "Alias", device.Alias)
        self.row_update_event(iter, "Icon", device.Icon)

    def device_add_event(self, device):
        if device.Fake:
            self.PrependDevice(device)
        else:
            self.AppendDevice(device)

    def row_update_event(self, iter, key, value):
        if key == "Trusted":
            if value:
                self.set(iter, trusted_icon=get_icon("blueman-trust", 16))
            else:
                self.set(iter, trusted_icon=None)


        elif key == "Paired":
            if value:
                self.set(iter, bonded_icon=get_icon("dialog-password", 16))
            else:
                self.set(iter, bonded_icon=None)

        elif key == "Fake":
            if value:
                self.set(iter, found_pb=get_icon("search", 16))
            else:
                self.set(iter, found_pb=None)

        elif key == "Alias":
            self.set(iter, caption=cgi.escape(value))

        elif key == "Icon":
            self.set(iter, device_pb=get_icon(value, 16))
