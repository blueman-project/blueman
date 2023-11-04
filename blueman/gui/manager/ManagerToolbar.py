from gettext import gettext as _
import logging
from typing import TYPE_CHECKING, Callable, Tuple, Optional

import gi

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerToolbar:
    def __init__(self, blueman: "Blueman") -> None:
        self.blueman = blueman

        self.blueman.List.connect("device-selected", self.on_device_selected)
        self.blueman.List.connect("device-property-changed", self.on_device_propery_changed)
        self.blueman.List.connect("adapter-changed", self.on_adapter_changed)
        self.blueman.List.connect("adapter-property-changed", self.on_adapter_property_changed)

        self.b_search = blueman.builder.get_widget("b_search", Gtk.ToolButton)
        self.b_search.connect("clicked", lambda button: blueman.inquiry())

        self.b_bond = blueman.builder.get_widget("b_bond", Gtk.ToolButton)
        self.b_bond.connect("clicked", self.on_action, self.blueman.bond)

        self.b_trust = blueman.builder.get_widget("b_trust", Gtk.ToolButton)
        self.b_trust.connect("clicked", self.on_action, self.blueman.toggle_trust)
        self.b_trust.set_homogeneous(False)

        self.b_trust.props.label = _("Untrust")
        (size, nsize) = Gtk.Widget.get_preferred_size(self.b_trust)
        self.b_trust.props.label = _("Trust")
        (size2, nsize2) = Gtk.Widget.get_preferred_size(self.b_trust)

        self.b_trust.props.width_request = max(size.width, size2.width)

        self.b_remove = blueman.builder.get_widget("b_remove", Gtk.ToolButton)
        self.b_remove.connect("clicked", self.on_action, self.blueman.remove)

        self.b_send = blueman.builder.get_widget("b_send", Gtk.ToolButton)
        self.b_send.props.sensitive = False
        self.b_send.connect("clicked", self.on_action, self.blueman.send)
        self.b_send.set_homogeneous(False)

        self.on_adapter_changed(blueman.List, blueman.List.get_adapter_path())

    def on_action(self, _button: Gtk.ToolButton, func: Callable[[Device], None]) -> None:
        device = self.blueman.List.get_selected_device()
        if device is not None:
            func(device)

    def on_adapter_property_changed(self, _lst: ManagerDeviceList, adapter: Adapter,
                                    key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if key == "Discovering" or key == "Powered":
            self._update_buttons(adapter)

    def on_adapter_changed(self, _lst: ManagerDeviceList, adapter_path: Optional[str]) -> None:
        logging.debug(f"toolbar adapter {adapter_path}")
        self._update_buttons(None if adapter_path is None else Adapter(obj_path=adapter_path))

    def on_device_selected(self, dev_list: ManagerDeviceList, device: Device, _tree_iter: Gtk.TreeIter) -> None:
        self._update_buttons(Adapter(obj_path=device["Adapter"]))

    def _update_buttons(self, adapter: Optional[Adapter]) -> None:
        powered = adapter is not None and adapter["Powered"]
        self.b_search.props.sensitive = powered and not (adapter and adapter["Discovering"])

        tree_iter = self.blueman.List.selected()
        if tree_iter is None:
            self.b_bond.props.sensitive = False
            self.b_trust.props.sensitive = False
            self.b_remove.props.sensitive = False
            self.b_send.props.sensitive = False
        else:
            row = self.blueman.List.get(tree_iter, "paired", "trusted", "objpush")
            self.b_bond.props.sensitive = powered and not row["paired"]
            self.b_trust.props.sensitive = True
            self.b_remove.props.sensitive = True
            self.b_send.props.sensitive = powered and row["objpush"]

            icon_name = "blueman-untrust-symbolic" if row["trusted"] else "blueman-trust-symbolic"
            self.b_trust.props.icon_widget = Gtk.Image(icon_name=icon_name, pixel_size=24, visible=True)
            self.b_trust.props.label = _("Untrust") if row["trusted"] else _("Trust")

    def on_device_propery_changed(self, dev_list: ManagerDeviceList, device: Device, tree_iter: Gtk.TreeIter,
                                  key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if dev_list.compare(tree_iter, dev_list.selected()):
            if key == "Trusted" or key == "Paired" or key == "UUIDs":
                self.on_device_selected(dev_list, device, tree_iter)
