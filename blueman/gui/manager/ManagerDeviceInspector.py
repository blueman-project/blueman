"""Selection-bound premium device inspector for the redesigned manager."""

from gettext import gettext as _

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Pango  # noqa: E402

from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceCards import (
    BrandSubtitle,
    DeviceCardAction,
    DeviceCardSnapshot,
    DeviceGroup,
    ManagerDeviceCards,
    apply_avatar,
    copy_button,
    set_state_class,
)


PRIMARY_TILES = {
    DeviceCardAction.SOUND_SETTINGS: ("audio-volume-high-symbolic", _("Play Sound")),
    DeviceCardAction.DISCONNECT: ("network-offline-symbolic", _("Disconnect")),
    DeviceCardAction.CONNECT: ("blueman-next-devices-symbolic", _("Connect")),
    DeviceCardAction.PAIR: ("list-add-symbolic", _("Pair")),
}


class ManagerDeviceInspector(Gtk.Box):
    __gsignals__ = {
        "action-requested": (GObject.SignalFlags.RUN_LAST, None, (str, str, object)),
    }

    def __init__(self, cards: ManagerDeviceCards) -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=16,
            width_request=410,
            visible=True,
        )
        self.cards = cards
        self.device_list = cards.device_list
        self._object_path: str | None = None
        self._primary_action = DeviceCardAction.CONNECT
        self.get_style_context().add_class("inspector-panel")

        self._empty = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=12,
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        empty_icon = Gtk.Image.new_from_icon_name("blueman-symbolic", Gtk.IconSize.DIALOG)
        empty_icon.get_style_context().add_class("inspector-empty-icon")
        empty_icon.show()
        empty_label = Gtk.Label(label=_("Select a device to view details"), wrap=True, visible=True)
        empty_label.get_style_context().add_class("inspector-subtitle")
        self._empty.pack_start(empty_icon, False, False, 0)
        self._empty.pack_start(empty_label, False, False, 0)
        self.pack_start(self._empty, True, True, 0)

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16, visible=True)
        self._content.pack_start(self._create_overview(), False, False, 0)
        self._content.pack_start(self._create_information(), False, False, 0)
        self._content.pack_start(self._create_quick_actions(), False, False, 0)
        self.pack_start(self._content, True, True, 0)

        self.device_list.connect("device-selected", self._on_selected)
        self.cards.connect("cards-changed", lambda _cards: self._refresh())
        selected = self.device_list.get_selected_device()
        self._object_path = selected.get_object_path() if selected is not None else None
        self._refresh()

    def do_get_preferred_width(self) -> tuple[int, int]:
        """Never ask for more than the column width.

        The slide revealer allocates its child at the natural width, so a long device
        name would otherwise push the panel past the window edge and clip it.
        """
        return self._cap_width(*Gtk.Box.do_get_preferred_width(self))

    def do_get_preferred_width_for_height(self, height: int) -> tuple[int, int]:
        return self._cap_width(*Gtk.Box.do_get_preferred_width_for_height(self, height))

    def _cap_width(self, minimum: int, natural: int) -> tuple[int, int]:
        request = self.get_size_request()[0]
        if request > 0:
            natural = max(minimum, min(natural, request))
        return minimum, natural

    def _create_overview(self) -> Gtk.Box:
        overview = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18, visible=True)
        overview.get_style_context().add_class("inspector-overview")

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16, visible=True)
        header.get_style_context().add_class("inspector-device-header")
        self._avatar = Gtk.Box(valign=Gtk.Align.CENTER, visible=True)
        self._avatar.get_style_context().add_class("inspector-avatar")
        self._icon = Gtk.Image(pixel_size=68, visible=True)
        self._avatar.pack_start(self._icon, True, True, 0)
        titles = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=4,
            valign=Gtk.Align.CENTER,
            hexpand=True,
            visible=True,
        )
        self._name = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, visible=True)
        self._name.set_max_width_chars(18)
        self._name.get_style_context().add_class("inspector-title")
        self._category = BrandSubtitle("inspector-subtitle")
        titles.pack_start(self._name, False, False, 0)
        titles.pack_start(self._category, False, False, 0)
        rename_icon = Gtk.Image.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.BUTTON)
        rename_icon.show()
        self._rename = Gtk.Button(
            image=rename_icon,
            valign=Gtk.Align.START,
            halign=Gtk.Align.END,
            visible=True,
        )
        self._rename.set_tooltip_text(_("Rename device"))
        self._rename.get_accessible().set_name(_("Rename device"))
        self._rename.get_style_context().add_class("inspector-edit-button")
        self._rename.connect("clicked", self._request, DeviceCardAction.RENAME)
        header.pack_start(self._avatar, False, False, 0)
        header.pack_start(titles, True, True, 0)
        header.pack_end(self._rename, False, False, 0)
        overview.pack_start(header, False, False, 0)

        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        status_bar.get_style_context().add_class("inspector-status-bar")
        self._status_dot = Gtk.Box(valign=Gtk.Align.CENTER, visible=True)
        self._status_dot.get_style_context().add_class("status-dot")
        self._status_text = Gtk.Label(xalign=0, visible=True)
        self._status_text.get_style_context().add_class("device-status")
        self._battery_separator = Gtk.Separator(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
        self._battery_separator.get_style_context().add_class("status-separator")
        self._battery_icon = Gtk.Image(pixel_size=16)
        self._battery_icon.get_style_context().add_class("battery-icon")
        self._battery_inline = Gtk.Label(xalign=0)
        self._battery_inline.get_style_context().add_class("battery-indicator")
        status_bar.pack_start(self._status_dot, False, False, 0)
        status_bar.pack_start(self._status_text, False, False, 0)
        status_bar.pack_start(self._battery_separator, False, False, 8)
        status_bar.pack_start(self._battery_icon, False, False, 0)
        status_bar.pack_start(self._battery_inline, False, False, 0)
        overview.pack_start(status_bar, False, False, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, homogeneous=True, visible=True)
        self._primary = self._action_tile("audio-volume-high-symbolic", _("Connect"), "primary-action-tile")
        self._send = self._action_tile("document-send-symbolic", _("Send File"), "action-tile")
        self._more = self._action_tile("view-more-horizontal-symbolic", _("More"), "action-tile")
        self._primary.connect("clicked", self._request_primary)
        self._send.connect("clicked", self._request, DeviceCardAction.SEND)
        self._more.connect("clicked", self._request, DeviceCardAction.MORE)
        for button in (self._primary, self._send, self._more):
            actions.pack_start(button, True, True, 0)
        overview.pack_start(actions, False, False, 0)
        return overview

    def _create_information(self) -> Gtk.Box:
        information = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, visible=True)
        information.get_style_context().add_class("inspector-section")
        info_title = Gtk.Label(label=_("Device Information"), xalign=0, visible=True)
        info_title.get_style_context().add_class("inspector-section-title")
        information.pack_start(info_title, False, False, 0)
        self._address = self._info_row(
            information, "bluetooth-symbolic", _("Address"),
            copy_button(lambda: self._address.get_text()),
        )
        self._brand_row, self._brand = self._info_row_widgets(information, "starred-symbolic", _("Brand"))
        self._type = self._info_row(information, "phone-symbolic", _("Type"))
        self._class = self._info_row(information, "view-grid-symbolic", _("Class"), last=True)
        return information

    def _create_quick_actions(self) -> Gtk.Box:
        quick = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, visible=True)
        quick.get_style_context().add_class("inspector-section")
        quick_title = Gtk.Label(label=_("Quick Actions"), xalign=0, visible=True)
        quick_title.get_style_context().add_class("inspector-section-title")
        quick.pack_start(quick_title, False, False, 0)
        self._sound_settings = Gtk.Button(visible=True)
        self._sound_settings.get_style_context().add_class("quick-action")
        self._sound_settings.add(self._quick_action_content("emblem-system-symbolic", _("Open Sound Settings")))
        self._sound_settings.connect("clicked", self._request, DeviceCardAction.SOUND_SETTINGS)
        quick.pack_start(self._sound_settings, False, False, 0)
        self._forget = Gtk.Button(visible=True)
        self._forget.get_style_context().add_class("quick-action")
        self._forget.get_style_context().add_class("quick-action-danger")
        self._forget.add(self._quick_action_content("user-trash-symbolic", _("Forget Device")))
        self._forget.connect("clicked", self._request, DeviceCardAction.REMOVE)
        quick.pack_start(self._forget, False, False, 0)
        return quick

    @staticmethod
    def _action_tile(icon_name: str, label: str, css_class: str) -> Gtk.Button:
        content = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=8,
            valign=Gtk.Align.CENTER,
            visible=True,
        )
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        text = Gtk.Label(label=label, visible=True)
        button = Gtk.Button(visible=True)
        button._tile_icon = icon  # type: ignore[attr-defined]
        button._tile_label = text  # type: ignore[attr-defined]
        icon.show()
        content.pack_start(icon, False, False, 0)
        content.pack_start(text, False, False, 0)
        button.add(content)
        button.get_accessible().set_name(label)
        button.get_style_context().add_class(css_class)
        return button

    @staticmethod
    def _quick_action_content(icon_name: str, text: str) -> Gtk.Box:
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14, visible=True)
        badge = Gtk.Box(valign=Gtk.Align.CENTER, visible=True)
        badge.get_style_context().add_class("quick-action-badge")
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        icon.show()
        badge.pack_start(icon, True, True, 0)
        label = Gtk.Label(label=text, xalign=0, visible=True)
        arrow = Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        arrow.get_style_context().add_class("quick-action-arrow")
        arrow.show()
        content.pack_start(badge, False, False, 0)
        content.pack_start(label, True, True, 0)
        content.pack_end(arrow, False, False, 0)
        return content

    @classmethod
    def _info_row(
        cls,
        parent: Gtk.Box,
        icon_name: str,
        label: str,
        suffix: Gtk.Widget | None = None,
        last: bool = False,
    ) -> Gtk.Label:
        return cls._info_row_widgets(parent, icon_name, label, suffix, last)[1]

    @staticmethod
    def _info_row_widgets(
        parent: Gtk.Box,
        icon_name: str,
        label: str,
        suffix: Gtk.Widget | None = None,
        last: bool = False,
    ) -> tuple[Gtk.Box, Gtk.Label]:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14, visible=True)
        row.get_style_context().add_class("inspector-row")
        if last:
            row.get_style_context().add_class("inspector-row-last")
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        icon.get_style_context().add_class("inspector-row-icon")
        key = Gtk.Label(label=label, xalign=0, visible=True)
        key.get_style_context().add_class("inspector-row-key")
        value = Gtk.Label(xalign=1, selectable=True, ellipsize=Pango.EllipsizeMode.END, visible=True)
        value.set_max_width_chars(20)
        value.get_style_context().add_class("inspector-row-value")
        icon.show()
        row.pack_start(icon, False, False, 0)
        row.pack_start(key, True, True, 0)
        if suffix is not None:
            row.pack_end(suffix, False, False, 0)
        row.pack_end(value, False, False, 0)
        parent.pack_start(row, False, False, 0)
        return row, value

    def _on_selected(self, _list: object, device: Device | None, _tree_iter: object) -> None:
        self._object_path = device.get_object_path() if device is not None else None
        self._refresh()

    def _refresh(self) -> None:
        card = self.cards.cards_by_path.get(self._object_path or "")
        if card is None:
            self._empty.show()
            self._content.hide()
            return
        self._empty.hide()
        self._content.show()
        self._show_snapshot(card.snapshot)

    def _show_snapshot(self, snapshot: DeviceCardSnapshot) -> None:
        self._icon.set_from_icon_name(snapshot.artwork, Gtk.IconSize.DIALOG)
        available = snapshot.group is DeviceGroup.AVAILABLE
        apply_avatar(self._avatar, snapshot)
        self._name.set_text(snapshot.name)
        self._name.set_tooltip_text(snapshot.name)
        self._category.update(snapshot)
        self._brand.set_text(snapshot.brand.name if snapshot.brand is not None else "")
        self._brand_row.set_visible(snapshot.brand is not None)
        self._address.set_text(snapshot.address)
        self._type.set_text(snapshot.category)
        self._class.set_text(snapshot.major_class)

        self._status_text.set_text(snapshot.status_label)
        state_class = "device-status-connected" if snapshot.connected else "device-status-disconnected"
        states = ("device-status-connected", "device-status-disconnected")
        set_state_class(self._status_text, state_class, states)
        set_state_class(self._status_dot, state_class, states)
        battery = snapshot.battery_label
        self._battery_inline.set_text(battery or "")
        if snapshot.battery_icon_name is not None:
            self._battery_icon.set_from_icon_name(snapshot.battery_icon_name, Gtk.IconSize.MENU)
        for widget in (self._battery_separator, self._battery_icon, self._battery_inline):
            widget.set_visible(battery is not None)

        self._primary_action = snapshot.primary_action
        icon_name, label = PRIMARY_TILES[self._primary_action]
        self._primary._tile_icon.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)  # type: ignore
        self._primary._tile_label.set_text(label)  # type: ignore[attr-defined]
        self._primary.get_accessible().set_name(f"{label} {snapshot.name}")
        self._send.set_visible(snapshot.can_send)
        self._more.set_visible(not available)
        self._sound_settings.set_visible(snapshot.audio)
        self._forget.set_visible(snapshot.paired)

    def _request_primary(self, button: Gtk.Button) -> None:
        if self.cards.cards_by_path.get(self._object_path or "") is not None:
            self._request(button, self._primary_action)

    def _request(self, button: Gtk.Button, action: DeviceCardAction) -> None:
        if self._object_path is not None:
            self.emit("action-requested", self._object_path, action.value, button)
