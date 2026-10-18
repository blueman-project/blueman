"""Premium three-panel shell around the existing Blueman manager backend."""

from __future__ import annotations

from dataclasses import dataclass
from gettext import gettext as _, ngettext

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GObject, Gtk  # noqa: E402


COMPACT_SIDEBAR_BREAKPOINT = 1050
NARROW_LAYOUT_BREAKPOINT = 1500
INSPECTOR_BREAKPOINT = 1180
SIDEBAR_WIDTH = 320
NARROW_SIDEBAR_WIDTH = 270
COMPACT_SIDEBAR_WIDTH = 76
INSPECTOR_WIDTH = 410
NARROW_INSPECTOR_WIDTH = 340


@dataclass(frozen=True)
class NavigationItem:
    label: str
    icon_name: str
    action: str | None


def navigation_items() -> tuple[NavigationItem, ...]:
    """Return the four primary destinations shown in the design."""
    return (
        NavigationItem(_("Devices"), "bluetooth-symbolic", None),
        NavigationItem(_("Scan"), "network-wireless-signal-excellent-symbolic", "app.inquiry"),
        NavigationItem(_("Files"), "document-send-symbolic", "app.send"),
        NavigationItem(_("Settings"), "emblem-system-symbolic", "app.settings"),
    )


def should_compact_sidebar(window_width: int) -> bool:
    return window_width < COMPACT_SIDEBAR_BREAKPOINT


def sidebar_width_for(window_width: int) -> int:
    if should_compact_sidebar(window_width):
        return COMPACT_SIDEBAR_WIDTH
    if window_width < NARROW_LAYOUT_BREAKPOINT:
        return NARROW_SIDEBAR_WIDTH
    return SIDEBAR_WIDTH


def inspector_width_for(window_width: int) -> int:
    return NARROW_INSPECTOR_WIDTH if window_width < NARROW_LAYOUT_BREAKPOINT else INSPECTOR_WIDTH


class ManagerWindowShell:
    """Compose the visible manager from modern GTK widgets.

    The Builder-owned legacy grid remains alive for backend/plugin compatibility,
    but it is deliberately not parented into the default presentation.
    """

    def __init__(
        self,
        window: Gtk.ApplicationWindow,
        content: Gtk.Widget,
        display_name: str,
    ) -> None:
        self.window = window
        self._legacy_content = content
        self._sidebar_labels: list[Gtk.Label] = []
        self._compact = False
        self._wide_inspector: bool | None = None
        self._legacy_view: Gtk.Widget | None = None
        self._card_view: Gtk.Widget | None = None
        self._inspector_revealer: Gtk.Revealer | None = None
        self._inspector: Gtk.Widget | None = None

        self.header = self._create_header(display_name)
        self.sidebar = self._create_sidebar(display_name)
        window.remove(content)

        self._dashboard = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            hexpand=True,
            vexpand=True,
            visible=True,
        )
        self._dashboard.get_style_context().add_class("device-dashboard")
        self._workspace = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self._workspace.set_hexpand(True)
        self._workspace.set_vexpand(True)
        self._workspace.set_visible(True)
        self._workspace.pack1(self._dashboard, resize=True, shrink=False)

        self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.main_paned.get_style_context().add_class("app-main")
        self.main_paned.pack1(self.sidebar, resize=False, shrink=False)
        self.main_paned.pack2(self._workspace, resize=True, shrink=False)
        self.main_paned.set_position(SIDEBAR_WIDTH)
        self.main_paned.show()

        window.set_titlebar(self.header)
        window.add(self.main_paned)
        window.connect("size-allocate", self._on_size_allocate)

    def _create_header(self, _display_name: str) -> Gtk.HeaderBar:
        header = Gtk.HeaderBar(
            show_close_button=True,
            visible=True,
        )
        header.set_custom_title(Gtk.Box(visible=True))
        header.get_style_context().add_class("app-header")

        self._status_icon = Gtk.Image.new_from_icon_name(
            "bluetooth-disabled", Gtk.IconSize.BUTTON
        )
        self._status_label = Gtk.Label(label=_("Bluetooth off"))
        self._inspector_toggle = Gtk.ToggleButton(sensitive=False)
        self._inspector_toggle.set_image(Gtk.Image.new_from_icon_name(
            "sidebar-show-symbolic", Gtk.IconSize.BUTTON
        ))
        self._inspector_toggle.set_tooltip_text(_("Show device details"))
        self._inspector_toggle.get_accessible().set_name(_("Toggle device details"))
        self._inspector_toggle.connect("toggled", self._on_inspector_toggled)
        header.pack_end(self._inspector_toggle)
        return header

    def install_device_cards(
        self,
        cards: Gtk.Widget,
        legacy_scrollview: Gtk.ScrolledWindow,
    ) -> None:
        """Install cards as the only visible dashboard; retain the classic model offscreen."""
        self._legacy_view = legacy_scrollview
        legacy_scrollview.hide()

        search = cards.search_entry
        parent = search.get_parent()
        if parent is not None:
            parent.remove(search)
        search.set_placeholder_text(_("Search devices, files, or actions…"))

        search_wrap = Gtk.Overlay(hexpand=True, visible=True)
        search_wrap.get_style_context().add_class("dashboard-search")
        search_wrap.add(search)
        shortcut = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
            halign=Gtk.Align.END,
            valign=Gtk.Align.CENTER,
            margin_end=12,
            visible=True,
        )
        for text in (_("Ctrl"), "K"):
            key = Gtk.Label(label=text, visible=True)
            key.get_style_context().add_class("shortcut-key")
            shortcut.pack_start(key, False, False, 0)
        search_wrap.add_overlay(shortcut)
        search_wrap.set_overlay_pass_through(shortcut, True)
        search.show()
        self._dashboard.pack_start(search_wrap, False, False, 0)

        heading = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            hexpand=True,
            visible=True,
        )
        heading.get_style_context().add_class("dashboard-header")
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, visible=True)
        title = Gtk.Label(label=_("Bluetooth Devices"), xalign=0, visible=True)
        title.get_style_context().add_class("dashboard-title")
        subtitle = Gtk.Label(
            label=_("Manage your connected devices, send files, and more."),
            xalign=0,
            visible=True,
        )
        subtitle.get_style_context().add_class("dashboard-subtitle")
        titles.pack_start(title, False, False, 0)
        titles.pack_start(subtitle, False, False, 0)
        pair = Gtk.Button(label=_("＋  Pair New Device"), visible=True)
        pair.set_action_name("app.inquiry")
        pair.get_style_context().add_class("primary-button")
        pair.get_style_context().add_class("pair-device-button")
        heading.pack_start(titles, True, True, 0)
        heading.pack_end(pair, False, False, 0)
        self._dashboard.pack_start(heading, False, False, 0)

        card_scrollview = Gtk.ScrolledWindow(
            hexpand=True,
            vexpand=True,
            overlay_scrolling=True,
            visible=True,
        )
        card_scrollview.get_style_context().add_class("dashboard-scroll")
        card_scrollview.add(cards)
        cards.show()
        self._dashboard.pack_start(card_scrollview, True, True, 0)
        self._card_view = card_scrollview

        if GObject.signal_lookup("cards-changed", cards.__gtype__):
            cards.connect("cards-changed", self._update_connected_count, cards)
        self._update_connected_count(cards, cards)

    def _update_connected_count(self, _source: object, cards: object) -> None:
        connected = sum(
            card.snapshot.connected for card in getattr(cards, "cards_by_path", {}).values()
        )
        self._identity_status.set_text(
            ngettext("%d device connected", "%d devices connected", connected) % connected
        )

    def install_device_inspector(self, inspector: Gtk.Widget) -> None:
        self._inspector = inspector
        revealer = Gtk.Revealer(
            transition_type=Gtk.RevealerTransitionType.SLIDE_LEFT,
            transition_duration=180,
            visible=True,
        )
        revealer.add(inspector)
        self._workspace.pack2(revealer, resize=False, shrink=False)
        self._inspector_revealer = revealer
        self._inspector_toggle.set_sensitive(True)
        wide = self.window.get_allocated_width() >= INSPECTOR_BREAKPOINT
        inspector.set_size_request(inspector_width_for(self.window.get_allocated_width()), -1)
        self._wide_inspector = wide
        self._inspector_toggle.set_active(wide)
        self._inspector_toggle.set_visible(not wide)
        revealer.set_reveal_child(wide)

    def _on_inspector_toggled(self, button: Gtk.ToggleButton) -> None:
        if self._inspector_revealer is not None:
            self._inspector_revealer.set_reveal_child(button.get_active())

    @staticmethod
    def _application_menu() -> Gio.Menu:
        menu = Gio.Menu()
        menu.append(_("Adapter"), "app.preferences")
        menu.append(_("Plugins"), "app.plugins")
        menu.append(_("Services"), "app.services")
        menu.append(_("About"), "app.about")
        menu.append(_("Quit"), "app.Quit")
        return menu

    @staticmethod
    def _icon_button(
        icon_name: str,
        tooltip: str,
        *,
        action: str | None = None,
        menu: Gio.Menu | None = None,
    ) -> Gtk.Button:
        image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        if menu is not None:
            button = Gtk.MenuButton(image=image, visible=True)
            button.set_menu_model(menu)
        else:
            button = Gtk.Button(image=image, visible=True)
            if action is not None:
                button.set_action_name(action)
        button.set_tooltip_text(tooltip)
        button.get_accessible().set_name(tooltip)
        image.show()
        return button

    def _create_sidebar(self, display_name: str) -> Gtk.Box:
        sidebar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            width_request=SIDEBAR_WIDTH,
            visible=True,
        )
        sidebar.get_style_context().add_class("app-sidebar")

        identity = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=13,
            margin_start=20,
            margin_end=16,
            margin_top=22,
            margin_bottom=18,
            visible=True,
        )
        identity.get_style_context().add_class("sidebar-identity")
        icon_tile = Gtk.Box(visible=True)
        icon_tile.get_style_context().add_class("brand-icon-tile")
        brand_icon = Gtk.Image.new_from_icon_name("blueman-symbolic", Gtk.IconSize.DIALOG)
        brand_icon.show()
        icon_tile.pack_start(brand_icon, True, True, 0)
        labels = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1, visible=True)
        brand = Gtk.Label(label=_("Bluetooth"), xalign=0, visible=True)
        brand.get_style_context().add_class("sidebar-brand-title")
        self._identity_status = Gtk.Label(label=_("0 devices connected"), xalign=0, visible=True)
        self._identity_status.get_style_context().add_class("sidebar-brand-subtitle")
        labels.pack_start(brand, False, False, 0)
        labels.pack_start(self._identity_status, False, False, 0)
        identity.pack_start(icon_tile, False, False, 0)
        identity.pack_start(labels, True, True, 0)
        self._sidebar_labels.extend((brand, self._identity_status))
        sidebar.pack_start(identity, False, False, 0)

        navigation = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_start=10,
            margin_end=10,
            visible=True,
        )
        for index, item in enumerate(navigation_items()):
            button = self._navigation_button(item)
            if index == 0:
                button.set_sensitive(False)
                button.get_style_context().add_class("sidebar-item-active")
            navigation.pack_start(button, False, False, 0)
        sidebar.pack_start(navigation, False, False, 0)

        power_card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            margin=14,
            visible=True,
        )
        power_card.get_style_context().add_class("sidebar-card")
        power_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        power_label = Gtk.Label(label=_("Bluetooth"), xalign=0, visible=True)
        power_label.get_style_context().add_class("sidebar-card-title")
        power_switch = Gtk.Switch(
            action_name="app.bluetooth_status",
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        power_switch.set_tooltip_text(_("Turn Bluetooth on or off"))
        power_switch.get_accessible().set_name(_("Bluetooth power"))
        power_top.pack_start(power_label, True, True, 0)
        power_top.pack_end(power_switch, False, False, 0)

        visible_label = Gtk.Label(label=_("Visible as\nThis computer"), xalign=0, visible=True)
        visible_label.get_style_context().add_class("sidebar-card-subtitle")
        radar = Gtk.Box(halign=Gtk.Align.CENTER, visible=True)
        radar.get_style_context().add_class("sidebar-radar")
        radar_icon = Gtk.Image.new_from_icon_name("blueman-symbolic", Gtk.IconSize.DIALOG)
        radar_icon.show()
        radar.pack_start(radar_icon, True, True, 0)
        power_card.pack_start(power_top, False, False, 0)
        power_card.pack_start(visible_label, False, False, 0)
        power_card.pack_start(radar, True, True, 0)
        self._sidebar_labels.extend((power_label, visible_label))
        sidebar.pack_end(power_card, False, False, 0)
        return sidebar

    def _navigation_button(self, item: NavigationItem) -> Gtk.Button:
        image = Gtk.Image.new_from_icon_name(item.icon_name, Gtk.IconSize.BUTTON)
        image.get_style_context().add_class("sidebar-item-image")
        label = Gtk.Label(label=item.label, xalign=0, visible=True)
        label.get_style_context().add_class("sidebar-item-label")
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, visible=True)
        image.show()
        box.pack_start(image, False, False, 0)
        box.pack_start(label, True, True, 0)
        button = Gtk.Button(visible=True, relief=Gtk.ReliefStyle.NONE)
        button.add(box)
        button.set_tooltip_text(item.label)
        button.get_accessible().set_name(item.label)
        button.get_style_context().add_class("sidebar-item")
        if item.action is not None:
            button.set_action_name(item.action)
        self._sidebar_labels.append(label)
        return button

    def set_bluetooth_state(self, enabled: bool) -> None:
        self._status_icon.set_from_icon_name(
            "bluetooth" if enabled else "bluetooth-disabled",
            Gtk.IconSize.BUTTON,
        )
        self._status_label.set_text(_("Bluetooth on") if enabled else _("Bluetooth off"))

    def _on_size_allocate(self, _window: Gtk.Widget, allocation: Gtk.Allocation) -> None:
        compact = should_compact_sidebar(allocation.width)
        width = sidebar_width_for(allocation.width)
        if compact != self._compact:
            self._compact = compact
            for label in self._sidebar_labels:
                label.set_visible(not compact)
        if self.sidebar.get_size_request()[0] != width:
            self.sidebar.set_size_request(width, -1)
        if self.main_paned.get_position() != width:
            self.main_paned.set_position(width)
        if self._inspector is not None:
            inspector_width = inspector_width_for(allocation.width)
            if self._inspector.get_size_request()[0] != inspector_width:
                self._inspector.set_size_request(inspector_width, -1)
        if self._inspector_revealer is not None:
            wide = allocation.width >= INSPECTOR_BREAKPOINT
            if wide != self._wide_inspector:
                self._wide_inspector = wide
                self._inspector_toggle.set_active(wide)
                self._inspector_toggle.set_visible(not wide)
