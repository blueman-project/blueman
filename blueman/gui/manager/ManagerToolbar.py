from gettext import gettext as _
import logging
from typing import TYPE_CHECKING, Callable, Tuple, Optional, Union

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

        self.b_search = blueman.builder.get_widget("b_search", Gtk.ToggleToolButton)
        self.b_search.connect("toggled", self.on_search_toggled)

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

    def _update_search_toggle(self, button: Gtk.ToggleToolButton, searching: bool) -> None:
        icon_widget: Union[Gtk.Image, Gtk.Spinner]
        if searching:
            icon_widget = Gtk.Spinner(visible=True)
            icon_widget.start()
            label = _("Searching")
            tooltip = _("Click to stop searching")
        else:
            icon_widget = Gtk.Image(icon_name="edit-find-symbolic", icon_size=Gtk.IconSize.LARGE_TOOLBAR, visible=True)
            label = _("Search")
            tooltip = _("Search for nearby devices")

        button.set_active(searching)
        button.set_icon_widget(icon_widget)
        button.set_label(label)
        button.set_tooltip_text(tooltip)

    def on_search_toggled(self, button: Gtk.ToggleToolButton) -> None:
        if not self.blueman.List.discovering and button.get_active():
            self.blueman.inquiry()
            self._update_search_toggle(button, True)
        elif self.blueman.List.discovering:
            self.blueman.List.stop_discovery()
            self._update_search_toggle(button, False)

    def on_adapter_property_changed(self, _lst: ManagerDeviceList, _adapter: Adapter,
                                    key_value: Tuple[str, object]) -> None:
        key, value = key_value
        if key == "Discovering":
            if value and not self.blueman.List.discovering:
                # It's not blueman discovering
                self.b_search.set_sensitive(False)
            elif not value:
                self.b_search.set_sensitive(True)

            # Block or we end in an infinite loop
            self.b_search.handler_block_by_func(self.on_search_toggled)
            self._update_search_toggle(self.b_search, True if value else False)
            self.b_search.handler_unblock_by_func(self.on_search_toggled)

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
