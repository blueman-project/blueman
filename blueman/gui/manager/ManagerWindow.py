"""Premium three-panel shell around the existing Blueman manager backend."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING
from gettext import gettext as _, ngettext

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Pango  # noqa: E402

from blueman.gui.theme.AnimationManager import start_animation, stop_animation_safe

if TYPE_CHECKING:
    DrawContext = cairo.Context[cairo.Surface]


COMPACT_SIDEBAR_BREAKPOINT = 1050
NARROW_LAYOUT_BREAKPOINT = 1500
INSPECTOR_BREAKPOINT = 1180
SIDEBAR_WIDTH = 320
NARROW_SIDEBAR_WIDTH = 270
COMPACT_SIDEBAR_WIDTH = 112
INSPECTOR_WIDTH = 410
NARROW_INSPECTOR_WIDTH = 340


class Page:
    DEVICES = "devices"
    SETTINGS = "settings"


PAGE_TRANSITION_MS = 260


def motion_duration(milliseconds: int) -> int:
    from blueman.gui.theme.ThemeManager import ThemeManager
    return 0 if ThemeManager.get_default().reduced_motion() else milliseconds


@dataclass(frozen=True)
class NavigationItem:
    label: str
    icon_name: str
    action: str | None
    page: str | None = None


def navigation_items() -> tuple[NavigationItem, ...]:
    """Return the four primary destinations shown in the design."""
    return (
        NavigationItem(_("Devices"), "blueman-next-devices-symbolic", None, Page.DEVICES),
        NavigationItem(_("Scan"), "blueman-next-scan-symbolic", "app.inquiry", Page.DEVICES),
        NavigationItem(_("Files"), "document-send-symbolic", "app.send"),
        NavigationItem(_("Settings"), "emblem-system-symbolic", None, Page.SETTINGS),
    )


class _RadarCanvas(Gtk.DrawingArea):
    """Prefers the full beacon size but can shrink, so short windows keep fitting."""

    def do_get_preferred_width(self) -> tuple[int, int]:
        return SidebarRadar.MIN_SIZE, SidebarRadar.MAX_SIZE

    def do_get_preferred_height(self) -> tuple[int, int]:
        return SidebarRadar.MIN_SIZE, SidebarRadar.MAX_SIZE


class SidebarRadar(Gtk.Overlay):
    """Concentric Bluetooth beacon; pulses only while discovery is running."""

    MAX_SIZE = 168
    MIN_SIZE = 112

    def __init__(self) -> None:
        super().__init__(visible=True)
        self.get_style_context().add_class("sidebar-radar")
        self._active = False
        self._phase = 0.0
        self._animation_source = 0
        self._canvas = _RadarCanvas(visible=True)
        self._canvas.connect("draw", self._on_draw)
        self.add(self._canvas)
        self._core = Gtk.Box(
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        self._core.get_style_context().add_class("sidebar-radar-core")
        glyph = Gtk.Image(icon_name="blueman-next-bluetooth-symbolic", pixel_size=36, visible=True)
        self._core.pack_start(glyph, True, True, 0)
        self.add_overlay(self._core)
        self.set_overlay_pass_through(self._core, True)
        self.connect("map", self._on_map)
        self.connect("unmap", self._on_unmap)
        self.connect("destroy", self._on_unmap)

    @property
    def active(self) -> bool:
        return self._active

    def set_active(self, active: bool) -> None:
        self._active = active
        if active and self.get_mapped() and not self._animation_source:
            self._animation_source = start_animation(33, self._tick, owner=self)
        elif not active:
            stop_animation_safe("_animation_source", self)
            self._phase = 0.0
            self._canvas.queue_draw()

    def _tick(self, _tick: int, elapsed: float) -> bool:
        self._phase = elapsed % 2.4 / 2.4
        self._canvas.queue_draw()
        return self._active

    def _on_draw(self, widget: Gtk.Widget, context: "DrawContext") -> bool:
        width, height = widget.get_allocated_width(), widget.get_allocated_height()
        cx, cy = width / 2, height / 2
        radius = min(width, height, self.MAX_SIZE) / 2
        accent = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        red, green, blue = accent.red, accent.green, accent.blue

        glow = cairo.RadialGradient(cx, cy, radius * 0.2, cx, cy, radius)
        glow.add_color_stop_rgba(0.0, red, green, blue, 0.30)
        glow.add_color_stop_rgba(0.55, red, green, blue, 0.10)
        glow.add_color_stop_rgba(1.0, red, green, blue, 0.0)
        context.set_source(glow)
        context.arc(cx, cy, radius, 0, math.tau)
        context.fill()

        context.set_line_width(1.0)
        for fraction, alpha in ((0.92, 0.10), (0.74, 0.16), (0.56, 0.24)):
            context.set_source_rgba(red, green, blue, alpha)
            context.arc(cx, cy, radius * fraction, 0, math.tau)
            context.stroke()

        if self._active:
            for offset in (0.0, 0.5):
                progress = (self._phase + offset) % 1.0
                context.set_line_width(2.0)
                context.set_source_rgba(red, green, blue, 0.45 * (1.0 - progress))
                context.arc(cx, cy, radius * (0.36 + 0.56 * progress), 0, math.tau)
                context.stroke()
        return False

    def _on_map(self, _widget: Gtk.Widget) -> None:
        if self._active and not self._animation_source:
            self._animation_source = start_animation(33, self._tick, owner=self)

    def _on_unmap(self, _widget: Gtk.Widget) -> None:
        stop_animation_safe("_animation_source", self)


def _drag_area(child: Gtk.Widget, window: Gtk.Window) -> Gtk.EventBox:
    """Wrap ``child`` so empty space moves the borderless window like a title bar."""
    area = Gtk.EventBox(visible=True)
    area.set_visible_window(False)
    area.add(child)

    def on_press(_area: Gtk.EventBox, event: Gdk.EventButton) -> bool:
        if event.button != Gdk.BUTTON_PRIMARY:
            return False
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            _toggle_maximized(window)
            return True
        window.begin_move_drag(event.button, int(event.x_root), int(event.y_root), event.time)
        return True

    area.connect("button-press-event", on_press)
    return area


def _toggle_maximized(window: Gtk.Window) -> None:
    if window.is_maximized():
        window.unmaximize()
    else:
        window.maximize()


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
        self._position_source = 0
        self._page = Page.DEVICES
        self._nav_buttons: dict[str, Gtk.Button] = {}

        self.header = self._create_titlebar()
        self._inspector_toggle = self._create_inspector_toggle()
        self.sidebar = self._create_sidebar()
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
        self.pages = Gtk.Stack(hexpand=True, vexpand=True, visible=True)
        self.pages.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        self.pages.set_transition_duration(PAGE_TRANSITION_MS)
        self.pages.get_style_context().add_class("app-pages")
        self.pages.add_named(self._dashboard, Page.DEVICES)
        self._workspace.pack1(self.pages, resize=True, shrink=False)

        self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.main_paned.get_style_context().add_class("app-main")
        # Shrinkable sides keep the window's minimum size below the compact breakpoints;
        # _on_size_allocate then switches to the compact sidebar and hidden inspector.
        self.main_paned.pack1(self.sidebar, resize=False, shrink=True)
        self.main_paned.pack2(self._workspace, resize=True, shrink=False)
        self.main_paned.set_position(SIDEBAR_WIDTH)
        self.main_paned.show()

        window.set_titlebar(self.header)
        window.add(self.main_paned)
        # Measure the content, not the toplevel: client-side shadows widen the window allocation.
        self.main_paned.connect("size-allocate", self._on_size_allocate)

    @staticmethod
    def _create_titlebar() -> Gtk.Box:
        """An empty titlebar keeps client-side decorations without a visible strip."""
        titlebar = Gtk.Box(visible=True)
        titlebar.get_style_context().add_class("app-titlebar")
        return titlebar

    def _create_inspector_toggle(self) -> Gtk.ToggleButton:
        toggle = Gtk.ToggleButton(sensitive=False, valign=Gtk.Align.CENTER)
        image = Gtk.Image.new_from_icon_name("sidebar-show-right-symbolic", Gtk.IconSize.BUTTON)
        image.show()
        toggle.set_image(image)
        toggle.set_tooltip_text(_("Show device details"))
        toggle.get_accessible().set_name(_("Toggle device details"))
        toggle.get_style_context().add_class("icon-button")
        toggle.connect("toggled", self._on_inspector_toggled)
        return toggle

    def _create_traffic_lights(self) -> Gtk.Box:
        lights = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=8,
            halign=Gtk.Align.START,
            visible=True,
        )
        lights.get_style_context().add_class("traffic-lights")
        self.traffic_light_buttons: dict[str, Gtk.Button] = {}
        for name, tooltip, callback in (
            ("close", _("Close"), lambda _b: self.window.close()),
            ("minimize", _("Minimize"), lambda _b: self.window.iconify()),
            ("maximize", _("Maximize"), lambda _b: _toggle_maximized(self.window)),
        ):
            button = Gtk.Button(visible=True, valign=Gtk.Align.CENTER)
            button.set_can_focus(False)
            button.get_style_context().add_class("traffic-light")
            button.get_style_context().add_class(f"tl-{name}")
            button.set_tooltip_text(tooltip)
            button.get_accessible().set_name(tooltip)
            button.connect("clicked", callback)
            lights.pack_start(button, False, False, 0)
            self.traffic_light_buttons[name] = button
        return lights

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
        search_wrap.get_style_context().add_class("search-wrap")
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
        search_row = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            hexpand=True,
            visible=True,
        )
        search_row.get_style_context().add_class("dashboard-search")
        search_row.pack_start(search_wrap, True, True, 0)
        search_row.pack_end(self._inspector_toggle, False, False, 0)
        self._dashboard.pack_start(_drag_area(search_row, self.window), False, False, 0)

        heading = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=20,
            hexpand=True,
            visible=True,
        )
        heading.get_style_context().add_class("dashboard-header")
        titles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, visible=True)
        title = Gtk.Label(label=_("Bluetooth Devices"), xalign=0, visible=True)
        title.get_style_context().add_class("dashboard-title")
        subtitle = Gtk.Label(
            label=_("Manage your connected devices, send files, and more."),
            xalign=0,
            wrap=True,
            visible=True,
        )
        subtitle.get_style_context().add_class("dashboard-subtitle")
        titles.pack_start(title, False, False, 0)
        titles.pack_start(subtitle, False, False, 0)
        pair = Gtk.Button(visible=True, valign=Gtk.Align.CENTER)
        pair_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        pair_icon = Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        pair_icon.show()
        pair_content.pack_start(pair_icon, False, False, 0)
        pair_content.pack_start(Gtk.Label(label=_("Pair New Device"), visible=True), False, False, 0)
        pair.add(pair_content)
        pair.set_action_name("app.inquiry")
        pair.get_accessible().set_name(_("Pair New Device"))
        pair.get_style_context().add_class("primary-button")
        pair.get_style_context().add_class("pair-device-button")
        heading.pack_start(titles, True, True, 0)
        heading.pack_end(pair, False, False, 0)
        self._dashboard.pack_start(_drag_area(heading, self.window), False, False, 0)

        card_scrollview = Gtk.ScrolledWindow(
            hexpand=True,
            vexpand=True,
            overlay_scrolling=True,
            hscrollbar_policy=Gtk.PolicyType.NEVER,
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
        revealer.get_style_context().add_class("inspector-column")
        scroller = Gtk.ScrolledWindow(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            vscrollbar_policy=Gtk.PolicyType.AUTOMATIC,
            visible=True,
        )
        scroller.get_style_context().add_class("inspector-scroll")
        scroller.add(inspector)
        revealer.add(scroller)
        self._workspace.pack2(revealer, resize=False, shrink=True)
        self._inspector_revealer = revealer
        self._inspector_toggle.set_sensitive(True)
        content_width = self.main_paned.get_allocated_width()
        wide = content_width >= INSPECTOR_BREAKPOINT
        inspector.set_size_request(inspector_width_for(content_width), -1)
        self._wide_inspector = wide
        self._inspector_toggle.set_active(wide)
        self._inspector_toggle.set_visible(not wide)
        self._update_inspector_reveal()

    def install_settings_page(self, page: Gtk.Widget) -> None:
        self.pages.add_named(page, Page.SETTINGS)

    @property
    def page(self) -> str:
        return self._page

    def show_page(self, name: str) -> None:
        """Slide between Devices and Settings; the inspector only belongs to Devices."""
        if self.pages.get_child_by_name(name) is None:
            return
        self._page = name
        self.pages.set_transition_duration(motion_duration(PAGE_TRANSITION_MS))
        self.pages.set_visible_child_name(name)
        for page, button in self._nav_buttons.items():
            context = button.get_style_context()
            if page == name:
                context.add_class("sidebar-item-active")
            else:
                context.remove_class("sidebar-item-active")
        self._update_inspector_reveal()

    def _update_inspector_reveal(self) -> None:
        if self._inspector_revealer is None:
            return
        self._inspector_revealer.set_transition_duration(motion_duration(180))
        self._inspector_revealer.set_reveal_child(
            self._page == Page.DEVICES and self._inspector_toggle.get_active()
        )

    def _on_inspector_toggled(self, _button: Gtk.ToggleButton) -> None:
        self._update_inspector_reveal()

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

    def _create_sidebar(self) -> Gtk.Box:
        sidebar = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            visible=True,
        )
        sidebar.get_style_context().add_class("app-sidebar")

        top = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, visible=True)
        lights = self._create_traffic_lights()
        lights.set_margin_start(20)
        lights.set_margin_top(18)
        top.pack_start(lights, False, False, 0)
        identity = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=14,
            margin_start=24,
            margin_end=16,
            margin_top=28,
            margin_bottom=26,
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
        top.pack_start(identity, False, False, 0)
        sidebar.pack_start(_drag_area(top, self.window), False, False, 0)

        navigation = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
            margin_start=18,
            margin_end=18,
            visible=True,
        )
        for item in navigation_items():
            button = self._navigation_button(item)
            if item.page is not None and item.action is None:
                self._nav_buttons[item.page] = button
            navigation.pack_start(button, False, False, 0)
        self._nav_buttons[Page.DEVICES].get_style_context().add_class("sidebar-item-active")
        sidebar.pack_start(navigation, False, False, 0)

        power_card = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin=18,
            visible=True,
        )
        power_card.get_style_context().add_class("sidebar-card")
        power_top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        power_label = Gtk.Label(label=_("Bluetooth"), xalign=0, visible=True)
        power_label.get_style_context().add_class("sidebar-card-title")
        self.power_switch = Gtk.Switch(
            action_name="app.bluetooth_status",
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        self.power_switch.set_tooltip_text(_("Turn Bluetooth on or off"))
        self.power_switch.get_accessible().set_name(_("Bluetooth power"))
        power_top.pack_start(power_label, True, True, 0)
        power_top.pack_end(self.power_switch, False, False, 0)

        visible_caption = Gtk.Label(label=_("Visible as"), xalign=0, visible=True)
        visible_caption.get_style_context().add_class("sidebar-card-subtitle")
        visible_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        self._adapter_name = Gtk.Label(
            label=_("This computer"),
            xalign=0,
            ellipsize=Pango.EllipsizeMode.END,
            visible=True,
        )
        self._adapter_name.get_style_context().add_class("sidebar-adapter-name")
        rename = self._icon_button(
            "document-edit-symbolic", _("Change adapter name"), action="app.preferences"
        )
        rename.get_style_context().add_class("flat-icon-button")
        visible_row.pack_start(self._adapter_name, True, True, 0)
        visible_row.pack_end(rename, False, False, 0)
        self.radar = SidebarRadar()
        power_card.pack_start(power_top, False, False, 0)
        power_card.pack_start(visible_caption, False, False, 0)
        power_card.pack_start(visible_row, False, False, 0)
        power_card.pack_start(self.radar, True, True, 0)
        self._power_card = power_card
        sidebar.pack_end(power_card, False, False, 0)
        return sidebar

    def set_adapter_name(self, name: str | None) -> None:
        self._adapter_name.set_text(name or _("This computer"))
        self._adapter_name.set_tooltip_text(name)

    def set_discovery_state(self, active: bool) -> None:
        self.radar.set_active(active)

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
        if item.page is not None:
            page = item.page
            button.connect("clicked", lambda _button: self.show_page(page))
        self._sidebar_labels.append(label)
        return button

    def set_bluetooth_state(self, enabled: bool) -> None:
        context = self.radar.get_style_context()
        if enabled:
            context.remove_class("sidebar-radar-off")
        else:
            context.add_class("sidebar-radar-off")
            self.radar.set_active(False)
        self.radar.queue_draw()

    def _apply_sidebar_width(self, width: int) -> bool:
        self._position_source = 0
        self.main_paned.set_position(width)
        return False

    def _on_size_allocate(self, _window: Gtk.Widget, allocation: Gtk.Allocation) -> None:
        compact = should_compact_sidebar(allocation.width)
        width = sidebar_width_for(allocation.width)
        if compact != self._compact:
            self._compact = compact
            for label in self._sidebar_labels:
                label.set_visible(not compact)
            self._power_card.set_visible(not compact)
        if self.main_paned.get_position() != width and not self._position_source:
            # Paned ignores position changes made while it is being allocated.
            self._position_source = GLib.idle_add(lambda: self._apply_sidebar_width(width))
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
