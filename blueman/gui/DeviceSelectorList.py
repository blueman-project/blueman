from html import escape
from typing import Optional, Any, List

from blueman.bluez.Device import Device
from blueman.gui.DeviceList import DeviceList
from gi.repository import Pango

import gi

from blueman.gui.GenericList import ListDataDict

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceSelectorList(DeviceList):
    def __init__(self, adapter_name: Optional[str] = None) -> None:
        tabledata: List[ListDataDict] = [
            # device picture
            {"id": "device_icon", "type": str, "renderer": Gtk.CellRendererPixbuf(stock_size=Gtk.IconSize.MENU),
             "render_attrs": {"icon_name": 0}},
            # device caption
            {"id": "caption", "type": str, "renderer": Gtk.CellRendererText(ellipsize=Pango.EllipsizeMode.END),
             "render_attrs": {"markup": 1},
             "view_props": {"expand": True}},
            {"id": "paired_icon", "type": str, "renderer": Gtk.CellRendererPixbuf(stock_size=Gtk.IconSize.MENU),
             "render_attrs": {"icon_name": 2}},
            {"id": "trusted_icon", "type": str, "renderer": Gtk.CellRendererPixbuf(stock_size=Gtk.IconSize.MENU),
             "render_attrs": {"icon_name": 3}}
        ]

        super().__init__(adapter_name, tabledata, headers_visible=False)

    def on_icon_theme_changed(self, _icon_them: Gtk.IconTheme) -> None:
        for row in self.liststore:
            device = self.get(row.iter, "device")["device"]
            self.row_setup_event(row.iter, device)

    def row_setup_event(self, tree_iter: Gtk.TreeIter, device: Device) -> None:
        self.row_update_event(tree_iter, "Trusted", device['Trusted'])
        self.row_update_event(tree_iter, "Paired", device['Paired'])
        self.row_update_event(tree_iter, "Alias", device['Alias'])
        self.row_update_event(tree_iter, "Icon", device['Icon'])

    def row_update_event(self, tree_iter: Gtk.TreeIter, key: str, value: Any) -> None:
        if key == "Trusted":
            if value:
                self.set(tree_iter, trusted_icon="blueman-trust")
            else:
                self.set(tree_iter, trusted_icon=None)

        elif key == "Paired":
            if value:
                self.set(tree_iter, paired_icon="dialog-password")
            else:
                self.set(tree_iter, paired_icon=None)

        elif key == "Alias":
            self.set(tree_iter, caption=escape(value))

        elif key == "Icon":
            self.set(tree_iter, device_icon=value)
