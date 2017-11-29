# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget


class DeviceSelectorDialog(Gtk.Dialog):
    def __init__(self, title=_("Select Device"), parent=None, discover=True, adapter_name=None):
        super(DeviceSelectorDialog, self).__init__(
            title, parent, 0, ("_Cancel", Gtk.ResponseType.REJECT, "_OK", Gtk.ResponseType.ACCEPT),
            icon_name="blueman", resizable=False, name="DeviceSelectorDialog"

        )

        self.vbox.props.halign = Gtk.Align.CENTER
        self.vbox.props.valign = Gtk.Align.CENTER
        self.vbox.props.hexpand = True
        self.vbox.props.vexpand = True
        self.vbox.props.margin = 6

        self.selector = DeviceSelectorWidget(adapter_name=adapter_name)
        self.selector.show()
        self.vbox.pack_start(self.selector, True, True, 0)

        self.selection = None

        self.selector.List.connect("device-selected", self.on_device_selected)
        self.selector.List.connect("adapter-changed", self.on_adapter_changed)
        if discover:
            self.selector.List.DiscoverDevices()

        self.selector.List.connect("row-activated", self.on_row_activated)

    def on_row_activated(self, treeview, path, view_column, *args):
        self.response(Gtk.ResponseType.ACCEPT)

    def on_adapter_changed(self, devlist, adapter):
        self.selection = None

    def on_device_selected(self, devlist, device, tree_iter):
        self.selection = (devlist.Adapter.get_object_path(), device)

    def GetSelection(self):
        if self.selection:
            return (self.selection[0], self.selection[1])
        else:
            return None
