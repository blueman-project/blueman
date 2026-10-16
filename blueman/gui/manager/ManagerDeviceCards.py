"""Card presentation synchronized with the legacy manager device model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from gettext import gettext as _
from typing import TYPE_CHECKING

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Pango  # noqa: E402

from blueman.bluez.Device import Device

if TYPE_CHECKING:
    from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList


class DeviceGroup(Enum):
    CONNECTED = "connected"
    PAIRED = "paired"
    AVAILABLE = "available"


def group_for_state(*, connected: bool, paired: bool) -> DeviceGroup:
    if connected:
        return DeviceGroup.CONNECTED
    if paired:
        return DeviceGroup.PAIRED
    return DeviceGroup.AVAILABLE


@dataclass(frozen=True)
class DeviceCardSnapshot:
    object_path: str
    name: str
    category: str
    address: str
    icon_name: str
    connected: bool
    paired: bool
    trusted: bool
    battery_percentage: float | None

    @property
    def group(self) -> DeviceGroup:
        return group_for_state(connected=self.connected, paired=self.paired)

    @property
    def battery_label(self) -> str | None:
        if self.battery_percentage is None:
            return None
        return f"{round(self.battery_percentage):d}%"


class DeviceCard(Gtk.ListBoxRow):
    """Read-only device summary; actions continue to use the TreeView model."""

    def __init__(self, snapshot: DeviceCardSnapshot) -> None:
        super().__init__(visible=True, selectable=True, activatable=False)
        self.snapshot = snapshot
        self.get_style_context().add_class("device-card")

        content = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=16,
            visible=True,
        )
        self._icon = Gtk.Image(pixel_size=48, visible=True)
        self._icon.get_style_context().add_class("device-avatar")
        content.pack_start(self._icon, False, False, 0)

        identity = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3,
            hexpand=True,
            visible=True,
        )
        self._name = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, visible=True)
        self._name.get_style_context().add_class("device-name")
        self._category = Gtk.Label(xalign=0, visible=True)
        self._category.get_style_context().add_class("device-subtitle")
        self._address = Gtk.Label(xalign=0, selectable=True, visible=True)
        self._address.get_style_context().add_class("device-mac")
        identity.pack_start(self._name, False, False, 0)
        identity.pack_start(self._category, False, False, 0)
        identity.pack_start(self._address, False, False, 0)
        content.pack_start(identity, True, True, 0)

        status_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            halign=Gtk.Align.END,
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        self._status = Gtk.Label(xalign=1, visible=True)
        self._status.get_style_context().add_class("device-status")
        self._battery = Gtk.Label(xalign=1)
        self._battery.get_style_context().add_class("battery-indicator")
        status_box.pack_start(self._status, False, False, 0)
        status_box.pack_start(self._battery, False, False, 0)
        content.pack_end(status_box, False, False, 0)
        self.add(content)
        self.update(snapshot)

    def update(self, snapshot: DeviceCardSnapshot) -> None:
        self.snapshot = snapshot
        self._icon.set_from_icon_name(snapshot.icon_name or "bluetooth", Gtk.IconSize.DIALOG)
        self._name.set_text(snapshot.name)
        self._name.set_tooltip_text(snapshot.name)
        self._category.set_text(snapshot.category)
        self._address.set_text(snapshot.address)
        self._status.set_text(_("Connected") if snapshot.connected else _("Disconnected"))
        self._status.get_style_context().remove_class("device-status-connected")
        self._status.get_style_context().remove_class("device-status-disconnected")
        self._status.get_style_context().add_class(
            "device-status-connected" if snapshot.connected else "device-status-disconnected"
        )
        card_context = self.get_style_context()
        card_context.remove_class("device-card-connected")
        card_context.remove_class("device-card-disconnected")
        card_context.add_class(
            "device-card-connected" if snapshot.connected else "device-card-disconnected"
        )
        battery = snapshot.battery_label
        self._battery.set_text(_("Battery: %s") % battery if battery is not None else "")
        self._battery.set_visible(battery is not None)
        self.get_accessible().set_name(f"{snapshot.name}, {self._status.get_text()}")

    def set_card_selected(self, selected: bool) -> None:
        context = self.get_style_context()
        if selected:
            context.add_class("device-card-selected")
        else:
            context.remove_class("device-card-selected")


class ManagerDeviceCards(Gtk.Box):
    """Mirror visible model rows and bridge card selection to TreeIter selection."""

    GROUP_TITLES = {
        DeviceGroup.CONNECTED: _("Connected"),
        DeviceGroup.PAIRED: _("Paired"),
        DeviceGroup.AVAILABLE: _("Available"),
    }

    def __init__(self, device_list: "ManagerDeviceList") -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=18, margin=24, visible=True)
        self.device_list = device_list
        self.cards_by_path: dict[str, DeviceCard] = {}
        self._sync_source = 0
        self._sections: dict[DeviceGroup, Gtk.ListBox] = {}
        self._signal_handlers: list[tuple[object, int]] = []

        for group in DeviceGroup:
            title = Gtk.Label(label=self.GROUP_TITLES[group], xalign=0, visible=True)
            title.get_style_context().add_class("section-title")
            cards = Gtk.ListBox(
                selection_mode=Gtk.SelectionMode.SINGLE,
                activate_on_single_click=False,
                visible=True,
            )
            cards.get_style_context().add_class("device-card-list")
            handler = cards.connect("row-selected", self._on_card_selected)
            self._signal_handlers.append((cards, handler))
            self._sections[group] = cards
            self.pack_start(title, False, False, 0)
            self.pack_start(cards, False, False, 0)

        for signal in ("row-inserted", "row-deleted", "rows-reordered"):
            handler = self.device_list.filter.connect(signal, self._schedule_structure_sync)
            self._signal_handlers.append((self.device_list.filter, handler))
        for signal, callback in (
            ("device-property-changed", self._on_device_property_changed),
            ("device-selected", self._on_tree_selection_changed),
        ):
            handler = self.device_list.connect(signal, callback)
            self._signal_handlers.append((self.device_list, handler))
        self.connect("destroy", self._on_destroy)
        self.sync_structure()

    def _snapshot(self, tree_iter: Gtk.TreeIter) -> DeviceCardSnapshot:
        row = self.device_list.get(
            tree_iter, "device", "alias", "connected", "paired", "trusted"
        )
        device: Device = row["device"]
        object_path = device.get_object_path()
        return DeviceCardSnapshot(
            object_path=object_path,
            name=row["alias"],
            category=self.device_list.get_device_class(device),
            address=device["Address"],
            icon_name=device["Icon"],
            connected=row["connected"],
            paired=row["paired"],
            trusted=row["trusted"],
            battery_percentage=self.device_list.get_battery_percentage(object_path),
        )

    def _visible_snapshots(self) -> list[DeviceCardSnapshot]:
        snapshots: list[DeviceCardSnapshot] = []
        tree_iter = self.device_list.filter.get_iter_first()
        while tree_iter is not None:
            child_iter = self.device_list.filter.convert_iter_to_child_iter(tree_iter)
            snapshots.append(self._snapshot(child_iter))
            tree_iter = self.device_list.filter.iter_next(tree_iter)
        return snapshots

    def sync_structure(self) -> bool:
        for cards in self._sections.values():
            for child in cards.get_children():
                cards.remove(child)
        self.cards_by_path.clear()

        for snapshot in self._visible_snapshots():
            card = DeviceCard(snapshot)
            self.cards_by_path[snapshot.object_path] = card
            self._sections[snapshot.group].add(card)
        self.show_all()
        self._sync_source = 0
        self._sync_selection()
        return GLib.SOURCE_REMOVE

    def _schedule_structure_sync(self, *_args: object) -> None:
        if not self._sync_source:
            self._sync_source = GLib.idle_add(self.sync_structure)

    def _on_device_property_changed(
        self,
        _device_list: "ManagerDeviceList",
        device: Device,
        tree_iter: Gtk.TreeIter,
        key_value: tuple[str, object],
    ) -> None:
        object_path = device.get_object_path()
        card = self.cards_by_path.get(object_path)
        if card is None:
            self._schedule_structure_sync()
            return
        snapshot = self._snapshot(tree_iter)
        if snapshot.group != card.snapshot.group:
            self._schedule_structure_sync()
        else:
            card.update(snapshot)

    def _on_card_selected(self, _list_box: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if not isinstance(row, DeviceCard):
            return
        child_iter = self.device_list.find_device_by_path(row.snapshot.object_path)
        if child_iter is None:
            return
        valid, filter_iter = self.device_list.filter.convert_child_iter_to_iter(child_iter)
        if valid:
            self.device_list.selection.select_iter(filter_iter)

    def _on_tree_selection_changed(
        self,
        _device_list: "ManagerDeviceList",
        device: Device | None,
        _tree_iter: Gtk.TreeIter | None,
    ) -> None:
        selected_path = device.get_object_path() if device is not None else None
        for object_path, card in self.cards_by_path.items():
            card.set_card_selected(object_path == selected_path)

    def _sync_selection(self) -> None:
        self._on_tree_selection_changed(
            self.device_list, self.device_list.get_selected_device(), self.device_list.selected()
        )

    def _on_destroy(self, _widget: Gtk.Widget) -> None:
        if self._sync_source:
            GLib.source_remove(self._sync_source)
            self._sync_source = 0
        for obj, handler in self._signal_handlers:
            obj.disconnect(handler)
        self._signal_handlers.clear()
