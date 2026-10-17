"""Card presentation synchronized with the legacy manager device model."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from gettext import gettext as _
from typing import TYPE_CHECKING

import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, GObject, Gtk, Pango  # noqa: E402

from blueman.bluez.Device import Device
from blueman.gui.theme.AnimationManager import start_animation, stop_animation_safe

if TYPE_CHECKING:
    from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList


class DeviceGroup(Enum):
    CONNECTED = "connected"
    PAIRED = "paired"
    AVAILABLE = "available"


class DeviceCardAction(Enum):
    PAIR = "pair"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    SEND = "send"
    MORE = "more"
    RENAME = "rename"
    REMOVE = "remove"


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
    can_send: bool
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
    """Device summary with actions routed through the existing manager handlers."""

    def __init__(
        self,
        snapshot: DeviceCardSnapshot,
        action_callback: Callable[["DeviceCard", DeviceCardAction, Gtk.Widget], None],
    ) -> None:
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

        trailing = Gtk.Box(
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
        status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        status.pack_end(self._battery, False, False, 0)
        status.pack_end(self._status, False, False, 0)
        trailing.pack_start(status, False, False, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, visible=True)
        actions.get_style_context().add_class("device-actions")
        self._primary_action = Gtk.Button(visible=True)
        self._primary_action.get_style_context().add_class("primary-button")
        self._primary_action.connect("clicked", self._emit_primary_action, action_callback)
        actions.pack_start(self._primary_action, False, False, 0)
        self._send_action = self._icon_button("document-send-symbolic", _("Send files"))
        self._send_action.connect(
            "clicked", lambda button: action_callback(self, DeviceCardAction.SEND, button)
        )
        actions.pack_start(self._send_action, False, False, 0)
        self._more_action = self._icon_button("view-more-symbolic", _("More device actions"))
        self._more_action.connect(
            "clicked", lambda button: action_callback(self, DeviceCardAction.MORE, button)
        )
        actions.pack_start(self._more_action, False, False, 0)
        trailing.pack_start(actions, False, False, 0)
        content.pack_end(trailing, False, False, 0)
        self.add(content)
        self.update(snapshot)

    @staticmethod
    def _icon_button(icon_name: str, accessible_name: str) -> Gtk.Button:
        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        image.show()
        button = Gtk.Button(image=image, visible=True)
        button.get_style_context().add_class("secondary-button")
        button.set_tooltip_text(accessible_name)
        button.get_accessible().set_name(accessible_name)
        return button

    def _emit_primary_action(
        self,
        button: Gtk.Button,
        action_callback: Callable[["DeviceCard", DeviceCardAction, Gtk.Widget], None],
    ) -> None:
        action = (
            DeviceCardAction.DISCONNECT if self.snapshot.connected
            else DeviceCardAction.CONNECT if self.snapshot.paired
            else DeviceCardAction.PAIR
        )
        action_callback(self, action, button)

    def update(self, snapshot: DeviceCardSnapshot) -> None:
        self.snapshot = snapshot
        self._icon.set_from_icon_name(snapshot.icon_name or "bluetooth", Gtk.IconSize.DIALOG)
        self._name.set_text(snapshot.name)
        self._name.set_tooltip_text(snapshot.name)
        self._category.set_text(snapshot.category)
        self._address.set_text(snapshot.address)
        status = _("Connected") if snapshot.connected else _("Paired") if snapshot.paired else _("Available")
        self._status.set_text(status)
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
        primary_label = _("Disconnect") if snapshot.connected else _("Connect") if snapshot.paired else _("Pair")
        self._primary_action.set_label(primary_label)
        self._primary_action.set_tooltip_text(_("%s %s") % (primary_label, snapshot.name))
        self._primary_action.get_accessible().set_name(_("%s %s") % (primary_label, snapshot.name))
        self._send_action.set_visible(snapshot.can_send)
        self.get_accessible().set_name(f"{snapshot.name}, {self._status.get_text()}")

    def set_card_selected(self, selected: bool) -> None:
        context = self.get_style_context()
        if selected:
            context.add_class("device-card-selected")
        else:
            context.remove_class("device-card-selected")


class DiscoveryRadar(Gtk.DrawingArea):
    """Small lifecycle-safe discovery pulse driven by observed scan state."""

    def __init__(self) -> None:
        super().__init__(width_request=48, height_request=48, visible=True)
        self._active = False
        self._phase = 0.0
        self._animation_source = 0
        self.connect("draw", self._on_draw)
        self.connect("map", self._on_map)
        self.connect("unmap", self._on_unmap)
        self.connect("destroy", self._on_destroy)

    def set_active(self, active: bool) -> None:
        self._active = active
        if active and self.get_mapped() and not self._animation_source:
            self._animation_source = start_animation(33, self._tick, owner=self)
        elif not active:
            stop_animation_safe("_animation_source", self)
            self._phase = 0.0
            self.queue_draw()

    def _tick(self, _tick: int, elapsed: float) -> bool:
        self._phase = elapsed % 1.5 / 1.5
        self.queue_draw()
        return self._active

    def _on_draw(self, _widget: Gtk.Widget, context: cairo.Context) -> bool:
        allocation = self.get_allocation()
        center_x, center_y = allocation.width / 2, allocation.height / 2
        color = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        context.set_line_width(1.5)
        for offset in (0.0, 0.33, 0.66):
            progress = (self._phase + offset) % 1.0
            context.set_source_rgba(color.red, color.green, color.blue, 0.55 * (1.0 - progress))
            context.arc(center_x, center_y, 5 + progress * 17, 0, math.tau)
            context.stroke()
        context.set_source_rgba(color.red, color.green, color.blue, 1.0)
        context.arc(center_x, center_y, 4, 0, math.tau)
        context.fill()
        return False

    def _on_map(self, _widget: Gtk.Widget) -> None:
        if self._active and not self._animation_source:
            self._animation_source = start_animation(33, self._tick, owner=self)

    def _on_unmap(self, _widget: Gtk.Widget) -> None:
        stop_animation_safe("_animation_source", self)

    def _on_destroy(self, _widget: Gtk.Widget) -> None:
        stop_animation_safe("_animation_source", self)


class ManagerDeviceCards(Gtk.Box):
    """Mirror visible model rows and bridge card selection to TreeIter selection."""

    __gsignals__ = {
        "action-requested": (
            GObject.SignalFlags.RUN_LAST,
            None,
            (str, str, object),
        ),
        "cards-changed": (GObject.SignalFlags.RUN_LAST, None, ()),
        "stop-discovery-requested": (GObject.SignalFlags.RUN_LAST, None, ()),
    }

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
        self._section_containers: dict[DeviceGroup, Gtk.Box] = {}
        self._section_titles: dict[DeviceGroup, Gtk.Label] = {}
        self._signal_handlers: list[tuple[object, int]] = []
        self._changing_selection = False

        self.search_entry = Gtk.SearchEntry(
            placeholder_text=_("Search devices by name or address"),
            visible=True,
        )
        self.search_entry.get_style_context().add_class("search-entry")
        self.search_entry.get_accessible().set_name(_("Search Bluetooth devices"))
        self.search_entry.connect("search-changed", self._on_search_changed)
        self.pack_start(self.search_entry, False, False, 0)

        discovery_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, visible=True)
        discovery_box.get_style_context().add_class("glass-panel")
        self._discovery_radar = DiscoveryRadar()
        self._discovery_label = Gtk.Label(label=_("Scanning for nearby devices…"), xalign=0, visible=True)
        self._stop_discovery = Gtk.Button(label=_("Stop"), visible=True)
        self._stop_discovery.get_style_context().add_class("secondary-button")
        self._stop_discovery.connect("clicked", lambda _button: self.emit("stop-discovery-requested"))
        discovery_box.pack_start(self._discovery_radar, False, False, 0)
        discovery_box.pack_start(self._discovery_label, True, True, 0)
        discovery_box.pack_end(self._stop_discovery, False, False, 0)
        self._discovery_revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_DOWN,
            transition_duration=180,
            visible=True,
        )
        self._discovery_revealer.add(discovery_box)
        self.pack_start(self._discovery_revealer, False, False, 0)

        for group in DeviceGroup:
            section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, visible=True)
            title = Gtk.Label(xalign=0, visible=True)
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
            self._section_containers[group] = section
            self._section_titles[group] = title
            section.pack_start(title, False, False, 0)
            section.pack_start(cards, False, False, 0)
            self.pack_start(section, False, False, 0)

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
            tree_iter, "device", "alias", "connected", "paired", "trusted", "objpush"
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
            can_send=row["objpush"],
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
            card = DeviceCard(snapshot, self._request_action)
            self.cards_by_path[snapshot.object_path] = card
            self._sections[snapshot.group].add(card)
        self.show_all()
        self._apply_search()
        self._sync_source = 0
        self._sync_selection()
        self.emit("cards-changed")
        return GLib.SOURCE_REMOVE

    def _apply_search(self) -> None:
        query = self.search_entry.get_text().strip().casefold()
        for card in self.cards_by_path.values():
            searchable = f"{card.snapshot.name} {card.snapshot.address}".casefold()
            card.set_visible(not query or query in searchable)
        for group, cards in self._sections.items():
            count = sum(card.get_visible() for card in cards.get_children())
            self._section_titles[group].set_text(_("%(group)s (%(count)d)") % {
                "group": self.GROUP_TITLES[group], "count": count
            })
            self._section_containers[group].set_visible(count > 0)

    def _on_search_changed(self, _entry: Gtk.SearchEntry) -> None:
        self._apply_search()

    def focus_search(self) -> None:
        self.search_entry.grab_focus()

    def set_discovery_state(self, active: bool, progress: float | None = None) -> None:
        self._discovery_revealer.set_reveal_child(active)
        self._discovery_radar.set_active(active)
        if active:
            if progress is None:
                self._discovery_label.set_text(_("Scanning for nearby devices…"))
            else:
                percent = max(0, min(100, round(progress * 100)))
                self._discovery_label.set_text(_("Scanning for nearby devices… %(progress)d%%") % {
                    "progress": percent
                })
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
            self._apply_search()
            self.emit("cards-changed")

    def _on_card_selected(self, _list_box: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if self._changing_selection or not isinstance(row, DeviceCard):
            return
        self._changing_selection = True
        for cards in self._sections.values():
            if cards is not _list_box:
                cards.unselect_all()
        self._changing_selection = False
        self._select_card_device(row)

    def _select_card_device(self, card: DeviceCard) -> bool:
        child_iter = self.device_list.find_device_by_path(card.snapshot.object_path)
        if child_iter is None:
            return False
        valid, filter_iter = self.device_list.filter.convert_child_iter_to_iter(child_iter)
        if valid:
            self.device_list.selection.select_iter(filter_iter)
        return valid

    def _request_action(
        self, card: DeviceCard, action: DeviceCardAction, anchor: Gtk.Widget
    ) -> None:
        if self._select_card_device(card):
            self.emit("action-requested", card.snapshot.object_path, action.value, anchor)

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
