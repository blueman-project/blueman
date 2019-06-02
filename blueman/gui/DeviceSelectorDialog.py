# coding=utf-8
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceSelectorDialog(Gtk.Dialog):
    def __init__(self, title=_("Select Device"), parent=None, discover=True, adapter_name=None):
        super().__init__(title=title, name="DeviceSelectorDialog", parent=parent, icon_name="blueman", resizable=False)
        self.add_buttons('_Cancel', Gtk.ResponseType.REJECT, '_OK', Gtk.ResponseType.ACCEPT)

        self.vbox.props.halign = Gtk.Align.CENTER
        self.vbox.props.valign = Gtk.Align.CENTER
        self.vbox.props.hexpand = True
        self.vbox.props.vexpand = True
        self.vbox.props.margin = 6

        self.selector = DeviceSelectorWidget(adapter_name=adapter_name, visible=True)
        self.vbox.pack_start(self.selector, True, True, 0)

        self.selection = None

        self.selector.List.connect("device-selected", self.on_device_selected)
        self.selector.List.connect("adapter-changed", self.on_adapter_changed)
        if discover:
            self.selector.List.discover_devices()

        self.selector.List.connect("row-activated", self.on_row_activated)

    def close(self):
        self.selector.destroy()
        super().close()

    def on_row_activated(self, treeview, path, view_column, *args):
        self.response(Gtk.ResponseType.ACCEPT)

    def on_adapter_changed(self, devlist, adapter):
        self.selection = None

    def on_device_selected(self, devlist, device, tree_iter):
        self.selection = (devlist.Adapter.get_object_path(), device)
