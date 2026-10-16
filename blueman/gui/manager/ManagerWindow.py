"""Compatible modern shell around the existing manager content."""

from __future__ import annotations

from dataclasses import dataclass
from gettext import gettext as _

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk  # noqa: E402


COMPACT_SIDEBAR_BREAKPOINT = 1050
SIDEBAR_WIDTH = 236
COMPACT_SIDEBAR_WIDTH = 76


@dataclass(frozen=True)
class NavigationItem:
    label: str
    icon_name: str
    action: str | None


def navigation_items() -> tuple[NavigationItem, ...]:
    """Return destinations backed by existing, functional actions."""
    return (
        NavigationItem(_("Devices"), "bluetooth-symbolic", None),
        NavigationItem(_("Scan for Devices"), "view-refresh-symbolic", "app.inquiry"),
        NavigationItem(_("Adapter"), "preferences-system-symbolic", "app.preferences"),
        NavigationItem(_("Services"), "emblem-system-symbolic", "app.services"),
        NavigationItem(_("Plugins"), "application-x-addon-symbolic", "app.plugins"),
    )


def should_compact_sidebar(window_width: int) -> bool:
    return window_width < COMPACT_SIDEBAR_BREAKPOINT


class ManagerWindowShell:
    """Add a header and responsive sidebar without replacing legacy widgets."""

    def __init__(
        self,
        window: Gtk.ApplicationWindow,
        content: Gtk.Widget,
        display_name: str,
    ) -> None:
        self.window = window
        self._sidebar_labels: list[Gtk.Label] = []
        self._compact = False

        self.header = self._create_header(display_name)
        self.sidebar = self._create_sidebar()
        window.remove(content)
        self.main_paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        self.main_paned.get_style_context().add_class("app-main")
        self.main_paned.pack1(self.sidebar, resize=False, shrink=False)
        self.main_paned.pack2(content, resize=True, shrink=False)
        self.main_paned.set_position(SIDEBAR_WIDTH)
        self.main_paned.show()

        window.set_titlebar(self.header)
        window.add(self.main_paned)
        window.connect("size-allocate", self._on_size_allocate)

    def _create_header(self, display_name: str) -> Gtk.HeaderBar:
        header = Gtk.HeaderBar(
            title=display_name,
            subtitle=_("Bluetooth device manager"),
            show_close_button=True,
            visible=True,
        )

        self._status_icon = Gtk.Image.new_from_icon_name(
            "bluetooth-disabled", Gtk.IconSize.BUTTON
        )
        self._status_label = Gtk.Label(label=_("Bluetooth off"))
        status = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6, visible=True)
        status.get_style_context().add_class("header-status")
        status.pack_start(self._status_icon, False, False, 0)
        status.pack_start(self._status_label, False, False, 0)
        self._status_icon.show()
        self._status_label.show()
        header.pack_start(status)

        header.pack_end(self._icon_button(
            "open-menu-symbolic", _("Application menu"), menu=self._application_menu()
        ))
        header.pack_end(self._icon_button(
            "preferences-system-symbolic", _("Adapter settings"), action="app.preferences"
        ))
        header.pack_end(self._icon_button(
            "edit-find-symbolic", _("Scan for devices"), action="app.inquiry"
        ))
        return header

    @staticmethod
    def _application_menu() -> Gio.Menu:
        menu = Gio.Menu()
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
            width_request=SIDEBAR_WIDTH,
            visible=True,
        )
        sidebar.get_style_context().add_class("app-sidebar")

        navigation = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            margin_top=16,
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
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin=12,
            visible=True,
        )
        power_card.get_style_context().add_class("sidebar-card")
        power_icon = Gtk.Image.new_from_icon_name("bluetooth-symbolic", Gtk.IconSize.BUTTON)
        power_label = Gtk.Label(label=_("Bluetooth"), xalign=0, visible=True)
        power_switch = Gtk.Switch(
            action_name="app.bluetooth_status",
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        power_switch.set_tooltip_text(_("Turn Bluetooth on or off"))
        power_switch.get_accessible().set_name(_("Bluetooth power"))
        power_icon.show()
        power_card.pack_start(power_icon, False, False, 0)
        power_card.pack_start(power_label, True, True, 0)
        power_card.pack_end(power_switch, False, False, 0)
        self._sidebar_labels.append(power_label)
        sidebar.pack_end(power_card, False, False, 0)
        return sidebar

    def _navigation_button(self, item: NavigationItem) -> Gtk.Button:
        image = Gtk.Image.new_from_icon_name(item.icon_name, Gtk.IconSize.BUTTON)
        label = Gtk.Label(label=item.label, xalign=0, visible=True)
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
        if compact == self._compact:
            return
        self._compact = compact
        width = COMPACT_SIDEBAR_WIDTH if compact else SIDEBAR_WIDTH
        self.sidebar.set_size_request(width, -1)
        self.main_paned.set_position(width)
        for label in self._sidebar_labels:
            label.set_visible(not compact)
