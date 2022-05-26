from gettext import gettext as _
from typing import Optional, Tuple

from blueman.bluez.Device import Device
from blueman.gui.DeviceList import DeviceList
from blueman.gui.DeviceSelectorWidget import DeviceSelectorWidget

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceSelectorDialog(Gtk.Dialog):
    def __init__(self, title: str = _("Select Device"), parent: Optional[Gtk.Container] = None, discover: bool = True,
                 adapter_name: Optional[str] = None) -> None:
        super().__init__(title=title, name="DeviceSelectorDialog", parent=parent, icon_name="blueman", resizable=False)
        self.add_buttons(_("_Cancel"), Gtk.ResponseType.REJECT, _("_OK"), Gtk.ResponseType.ACCEPT)

        self.vbox.props.halign = Gtk.Align.CENTER
        self.vbox.props.valign = Gtk.Align.CENTER
        self.vbox.props.hexpand = True
        self.vbox.props.vexpand = True
        self.vbox.props.margin = 6

        self.selector = DeviceSelectorWidget(adapter_name=adapter_name, visible=True)
        self.vbox.pack_start(self.selector, True, True, 0)

        self.selection: Optional[Tuple[str, Device]] = None

        self.selector.List.connect("device-selected", self.on_device_selected)
        self.selector.List.connect("adapter-changed", self.on_adapter_changed)
        if discover:
            self.selector.List.discover_devices()

        self.selector.List.connect("row-activated", self.on_row_activated)

    def close(self) -> None:
        self.selector.destroy()
        super().close()

    def on_row_activated(self, _treeview: Gtk.TreeView, _path: Gtk.TreePath, _view_column: Gtk.TreeViewColumn,
                         *_args: object) -> None:
        self.response(Gtk.ResponseType.ACCEPT)

    def on_adapter_changed(self, _devlist: DeviceList, _adapter: str) -> None:
        self.selection = None

    def on_device_selected(self, devlist: DeviceList, device: Device, _tree_iter: Gtk.TreeIter) -> None:
        assert devlist.Adapter is not None
        self.selection = (devlist.Adapter.get_object_path(), device)
