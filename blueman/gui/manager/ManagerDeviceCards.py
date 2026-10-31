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
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, GObject, Gtk, Pango  # noqa: E402

from blueman.bluez.Device import Device
from blueman.DeviceClass import get_major_class
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
    SOUND_SETTINGS = "sound-settings"


AUDIO_MAJOR_CLASS = 4


def is_audio_device(klass: int, icon_name: str) -> bool:
    """Audio/video major class, or an audio icon for LE devices that report no class."""
    return (klass >> 8) & 0x1F == AUDIO_MAJOR_CLASS or icon_name.startswith("audio")


def major_class_name(klass: int) -> str:
    return get_major_class(klass) if klass else _("Unknown")


def group_for_state(*, connected: bool, paired: bool) -> DeviceGroup:
    if connected:
        return DeviceGroup.CONNECTED
    if paired:
        return DeviceGroup.PAIRED
    return DeviceGroup.AVAILABLE


def illustration_icon_name(category: str, fallback: str) -> str:
    """Choose bundled category artwork without claiming product-specific art."""
    normalized = category.casefold()
    if "head" in normalized:
        return "blueman-next-headphones"
    if "speaker" in normalized or "loud" in normalized:
        return "blueman-next-speaker"
    return fallback or "bluetooth"


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
    major_class: str = ""
    audio: bool = False

    @property
    def group(self) -> DeviceGroup:
        return group_for_state(connected=self.connected, paired=self.paired)

    @property
    def status_label(self) -> str:
        return _("Connected") if self.connected else _("Paired") if self.paired else _("Available")

    @property
    def primary_action(self) -> DeviceCardAction:
        """The headline action for this state: sound for connected audio, otherwise the next link step."""
        if self.connected:
            return DeviceCardAction.SOUND_SETTINGS if self.audio else DeviceCardAction.DISCONNECT
        return DeviceCardAction.CONNECT if self.paired else DeviceCardAction.PAIR

    @property
    def card_actions(self) -> tuple[DeviceCardAction, ...]:
        if self.group is DeviceGroup.AVAILABLE:
            return (DeviceCardAction.PAIR,)
        return (self.primary_action, DeviceCardAction.MORE)

    @property
    def battery_icon_name(self) -> str | None:
        if self.battery_percentage is None:
            return None
        level = max(0, min(100, int(round(self.battery_percentage / 10.0)) * 10))
        return f"battery-level-{level}-symbolic"

    @property
    def battery_label(self) -> str | None:
        if self.battery_percentage is None:
            return None
        return f"{round(self.battery_percentage):d}%"


ACTION_PRESENTATION = {
    DeviceCardAction.SOUND_SETTINGS: ("audio-volume-high-symbolic", _("Open sound settings")),
    DeviceCardAction.DISCONNECT: ("network-offline-symbolic", _("Disconnect")),
    DeviceCardAction.MORE: ("view-more-horizontal-symbolic", _("More device actions")),
}

AVATAR_CLASSES = (
    "device-avatar-speaker", "device-avatar-headphones", "device-avatar-phone",
    "device-avatar-keyboard", "device-avatar-mouse", "device-avatar-controller",
    "device-avatar-computer", "device-avatar-unknown", "device-avatar-available",
)


def avatar_class_for(category: str) -> str:
    category = category.casefold()
    return (
        "device-avatar-headphones" if "head" in category
        else "device-avatar-speaker" if "speaker" in category or "loud" in category
        else "device-avatar-phone" if "phone" in category
        else "device-avatar-keyboard" if "keyboard" in category
        else "device-avatar-mouse" if "mouse" in category
        else "device-avatar-controller" if "controller" in category or "game" in category
        else "device-avatar-computer" if "computer" in category
        else "device-avatar-unknown"
    )


def copy_to_clipboard(text: str) -> None:
    clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
    clipboard.set_text(text, -1)
    clipboard.store()


def copy_button(get_text: Callable[[], str]) -> Gtk.Button:
    """Small inline button that copies a value such as a device address."""
    image = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.MENU)
    image.show()
    button = Gtk.Button(image=image, valign=Gtk.Align.CENTER, visible=True)
    button.set_relief(Gtk.ReliefStyle.NONE)
    button.get_style_context().add_class("copy-button")
    button.set_tooltip_text(_("Copy address"))
    button.get_accessible().set_name(_("Copy address"))
    button.connect("clicked", lambda _button: copy_to_clipboard(get_text()))
    return button


def set_state_class(widget: Gtk.Widget, active: str, choices: tuple[str, ...]) -> None:
    context = widget.get_style_context()
    for css_class in choices:
        context.remove_class(css_class)
    context.add_class(active)


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
            spacing=20,
            visible=True,
        )
        avatar = Gtk.Box(valign=Gtk.Align.CENTER, visible=True)
        avatar.get_style_context().add_class("device-avatar")
        self._avatar = avatar
        self._icon = Gtk.Image(pixel_size=56, visible=True)
        avatar.pack_start(self._icon, True, True, 0)
        content.pack_start(avatar, False, False, 0)

        identity = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=2,
            hexpand=True,
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        self._name = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, visible=True)
        self._name.get_style_context().add_class("device-name")
        self._category = Gtk.Label(xalign=0, visible=True)
        self._category.get_style_context().add_class("device-subtitle")
        address_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4, visible=True)
        self._address = Gtk.Label(xalign=0, selectable=True, visible=True)
        self._address.get_style_context().add_class("device-mac")
        address_row.pack_start(self._address, False, False, 0)
        address_row.pack_start(copy_button(lambda: self.snapshot.address), False, False, 0)
        identity.pack_start(self._name, False, False, 0)
        identity.pack_start(self._category, False, False, 0)
        identity.pack_start(address_row, False, False, 0)

        self._status_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        self._status_row.get_style_context().add_class("device-status-row")
        self._status_dot = Gtk.Box(valign=Gtk.Align.CENTER, visible=True)
        self._status_dot.get_style_context().add_class("status-dot")
        self._status = Gtk.Label(xalign=0, visible=True)
        self._status.get_style_context().add_class("device-status")
        self._battery_icon = Gtk.Image(pixel_size=16)
        self._battery_icon.get_style_context().add_class("battery-icon")
        self._battery = Gtk.Label(xalign=0)
        self._battery.get_style_context().add_class("battery-indicator")
        self._status_row.pack_start(self._status_dot, False, False, 0)
        self._status_row.pack_start(self._status, False, False, 0)
        self._status_row.pack_start(self._battery_icon, False, False, 6)
        self._status_row.pack_start(self._battery, False, False, 0)
        identity.pack_start(self._status_row, False, False, 0)
        content.pack_start(identity, True, True, 0)

        actions = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=14,
            halign=Gtk.Align.END,
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        actions.get_style_context().add_class("device-actions")
        self._action_buttons: dict[DeviceCardAction, Gtk.Button] = {}
        for action in (DeviceCardAction.CONNECT, DeviceCardAction.PAIR):
            button = Gtk.Button(label=_("Connect") if action is DeviceCardAction.CONNECT else _("Pair"))
            button.get_style_context().add_class("pill-button")
            self._action_buttons[action] = button
        for action, (icon_name, tooltip) in ACTION_PRESENTATION.items():
            self._action_buttons[action] = self._icon_button(icon_name, tooltip)
        for action, button in self._action_buttons.items():
            button.connect("clicked", lambda b, a=action: action_callback(self, a, b))
            actions.pack_start(button, False, False, 0)
        content.pack_end(actions, False, False, 0)
        self.add(content)
        self.update(snapshot)

    @staticmethod
    def _icon_button(icon_name: str, accessible_name: str) -> Gtk.Button:
        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        image.show()
        button = Gtk.Button(image=image)
        button.get_style_context().add_class("round-icon-button")
        button.set_tooltip_text(accessible_name)
        button.get_accessible().set_name(accessible_name)
        return button

    @property
    def visible_actions(self) -> tuple[DeviceCardAction, ...]:
        return tuple(action for action, button in self._action_buttons.items() if button.get_visible())

    def update(self, snapshot: DeviceCardSnapshot) -> None:
        self.snapshot = snapshot
        self._icon.set_from_icon_name(
            illustration_icon_name(snapshot.category, snapshot.icon_name),
            Gtk.IconSize.DIALOG,
        )
        available = snapshot.group is DeviceGroup.AVAILABLE
        avatar_context = self._avatar.get_style_context()
        for css_class in AVATAR_CLASSES:
            avatar_context.remove_class(css_class)
        avatar_context.add_class("device-avatar-available" if available else avatar_class_for(snapshot.category))

        self._name.set_text(snapshot.name)
        self._name.set_tooltip_text(snapshot.name)
        self._category.set_text(snapshot.category)
        self._address.set_text(snapshot.address)
        self._status.set_text(snapshot.status_label)
        state_class = "device-status-connected" if snapshot.connected else "device-status-disconnected"
        states = ("device-status-connected", "device-status-disconnected")
        set_state_class(self._status, state_class, states)
        set_state_class(self._status_dot, state_class, states)
        set_state_class(
            self,
            "device-card-connected" if snapshot.connected else "device-card-disconnected",
            ("device-card-connected", "device-card-disconnected"),
        )
        # Available devices are not linked yet; the mockup omits their status line.
        self._status_row.set_visible(not available)

        battery = snapshot.battery_label
        self._battery.set_text(battery or "")
        self._battery.set_visible(battery is not None)
        if snapshot.battery_icon_name is not None:
            self._battery_icon.set_from_icon_name(snapshot.battery_icon_name, Gtk.IconSize.MENU)
        self._battery_icon.set_visible(snapshot.battery_icon_name is not None)

        wanted = snapshot.card_actions
        for action, button in self._action_buttons.items():
            button.set_visible(action in wanted)
            if action in (DeviceCardAction.CONNECT, DeviceCardAction.PAIR,
                          DeviceCardAction.DISCONNECT, DeviceCardAction.SOUND_SETTINGS):
                label = button.get_tooltip_text() or button.get_label() or ""
                button.get_accessible().set_name(f"{label} {snapshot.name}")
        self.get_accessible().set_name(f"{snapshot.name}, {snapshot.status_label}")

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
        DeviceGroup.AVAILABLE: _("Available Devices"),
    }

    def __init__(self, device_list: "ManagerDeviceList") -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=20,
            hexpand=True,
            margin_start=28,
            margin_end=28,
            margin_bottom=28,
            visible=True,
        )
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
            section = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=8,
                hexpand=True,
                visible=True,
            )
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
            header.get_style_context().add_class("section-header")
            title = Gtk.Label(xalign=0, valign=Gtk.Align.CENTER, visible=True)
            title.get_style_context().add_class("section-title")
            header.pack_start(title, True, True, 0)
            if group is DeviceGroup.AVAILABLE:
                refresh = DeviceCard._icon_button("view-refresh-symbolic", _("Search for devices"))
                refresh.set_action_name("app.inquiry")
                refresh.get_style_context().add_class("section-action")
                refresh.show()
                header.pack_end(refresh, False, False, 0)
            cards = Gtk.ListBox(
                selection_mode=Gtk.SelectionMode.SINGLE,
                activate_on_single_click=False,
                hexpand=True,
                visible=True,
            )
            cards.get_style_context().add_class("device-card-list")
            handler = cards.connect("row-selected", self._on_card_selected)
            self._signal_handlers.append((cards, handler))
            self._sections[group] = cards
            self._section_containers[group] = section
            self._section_titles[group] = title
            section.pack_start(header, False, False, 0)
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
        klass = device["Class"]
        icon_name = device["Icon"]
        return DeviceCardSnapshot(
            object_path=object_path,
            name=row["alias"],
            category=self.device_list.get_device_class(device),
            address=device["Address"],
            icon_name=icon_name,
            connected=row["connected"],
            paired=row["paired"],
            trusted=row["trusted"],
            can_send=row["objpush"],
            battery_percentage=self.device_list.get_battery_percentage(object_path),
            major_class=major_class_name(klass),
            audio=is_audio_device(klass, icon_name),
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
        self._apply_search()
        self._sync_source = 0
        if self.device_list.get_selected_device() is None and self.cards_by_path:
            self._select_card_device(next(iter(self.cards_by_path.values())))
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
