from gettext import gettext as _
import logging
from typing import TYPE_CHECKING, Tuple, Optional, Any

import gi

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gio

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
        self.b_bond = blueman.builder.get_widget("b_bond", Gtk.ToolButton)
        self.b_trust = blueman.builder.get_widget("b_trust", Gtk.ToolButton)
        self.b_remove = blueman.builder.get_widget("b_remove", Gtk.ToolButton)
        self.b_send = blueman.builder.get_widget("b_send", Gtk.ToolButton)

        self.blueman.register_action("bond", self._simple_actions)
        self.blueman.register_action("trust", self._simple_actions)

        self.b_trust.props.label = _("Untrust")
        (size, nsize) = Gtk.Widget.get_preferred_size(self.b_trust)
        self.b_trust.props.label = _("Trust")
        (size2, nsize2) = Gtk.Widget.get_preferred_size(self.b_trust)

        self.b_trust.props.width_request = max(size.width, size2.width)

        self.blueman.register_action("remove", self._simple_actions)
        self.blueman.register_action("sendfile", self._simple_actions)

        self.on_adapter_changed(blueman.List, blueman.List.get_adapter_path())

    def _simple_actions(self, action: Gio.Action, _val: Optional[Any]) -> None:
        device = self.blueman.List.get_selected_device()
        if device is not None:
            name = action.get_name()
            if name == "bond":
                self.blueman.bond(device)
            elif name == "trust":
                self.blueman.toggle_trust(device)
            elif name == "remove":
                self.blueman.remove(device)
            elif name == "sendfile":
                self.blueman.send(device)

    def on_adapter_property_changed(self, _lst: ManagerDeviceList, _adapter: Adapter,
                                    key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if key == "Discovering":
            if value:
                self.b_search.props.sensitive = False
            else:
                self.b_search.props.sensitive = True

    def on_adapter_changed(self, _lst: ManagerDeviceList, adapter_path: Optional[str]) -> None:
        logging.debug(f"toolbar adapter {adapter_path}")
        if adapter_path is None:
            self.b_search.props.sensitive = False
            self.b_send.props.sensitive = False
        else:
            self.b_search.props.sensitive = True

    def on_device_selected(self, dev_list: ManagerDeviceList, device: Device, tree_iter: Gtk.TreeIter) -> None:
        if device is None or tree_iter is None:
            self.b_bond.props.sensitive = False
            self.b_remove.props.sensitive = False
            self.b_trust.props.sensitive = False
        else:
            row = dev_list.get(tree_iter, "paired", "trusted", "objpush")
            self.b_remove.props.sensitive = True
            if row["paired"]:
                self.b_bond.props.sensitive = False
            else:
                self.b_bond.props.sensitive = True

            if row["trusted"]:
                image = Gtk.Image(icon_name="blueman-untrust-symbolic", pixel_size=24, visible=True)
                self.b_trust.props.icon_widget = image
                self.b_trust.props.sensitive = True
                self.b_trust.props.label = _("Untrust")

            else:
                image = Gtk.Image(icon_name="blueman-trust-symbolic", pixel_size=24, visible=True)
                self.b_trust.props.icon_widget = image
                self.b_trust.props.sensitive = True
                self.b_trust.props.label = _("Trust")

            if row["objpush"]:
                self.b_send.props.sensitive = True
            else:
                self.b_send.props.sensitive = False

    def on_device_propery_changed(self, dev_list: ManagerDeviceList, device: Device, tree_iter: Gtk.TreeIter,
                                  key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if dev_list.compare(tree_iter, dev_list.selected()):
            if key == "Trusted" or key == "Paired" or key == "UUIDs":
                self.on_device_selected(dev_list, device, tree_iter)
