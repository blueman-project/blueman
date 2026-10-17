"""Selection-bound premium device inspector for the redesigned manager."""

from gettext import gettext as _

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Pango  # noqa: E402

from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceCards import DeviceCardAction, ManagerDeviceCards


class ManagerDeviceInspector(Gtk.Box):
    __gsignals__ = {
        "action-requested": (GObject.SignalFlags.RUN_LAST, None, (str, str, object)),
    }

    def __init__(self, cards: ManagerDeviceCards) -> None:
        super().__init__(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=14,
            margin=16,
            width_request=352,
            visible=True,
        )
        self.cards = cards
        self.device_list = cards.device_list
        self._object_path: str | None = None
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

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)

        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14, visible=True)
        header.get_style_context().add_class("inspector-device-header")
        avatar = Gtk.Box(visible=True)
        avatar.get_style_context().add_class("inspector-avatar")
        self._icon = Gtk.Image(pixel_size=58, visible=True)
        avatar.pack_start(self._icon, True, True, 0)
        titles = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=3,
            valign=Gtk.Align.CENTER,
            hexpand=True,
            visible=True,
        )
        self._name = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, visible=True)
        self._name.get_style_context().add_class("inspector-title")
        self._category = Gtk.Label(xalign=0, visible=True)
        self._category.get_style_context().add_class("inspector-subtitle")
        titles.pack_start(self._name, False, False, 0)
        titles.pack_start(self._category, False, False, 0)
        rename_icon = Gtk.Image.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.BUTTON)
        rename_icon.show()
        rename = Gtk.Button(image=rename_icon, visible=True)
        rename.set_tooltip_text(_("Rename device"))
        rename.get_style_context().add_class("inspector-edit-button")
        rename.connect("clicked", self._request, DeviceCardAction.RENAME)
        header.pack_start(avatar, False, False, 0)
        header.pack_start(titles, True, True, 0)
        header.pack_end(rename, False, False, 0)
        self._content.pack_start(header, False, False, 0)

        status_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        status_bar.get_style_context().add_class("inspector-status-bar")
        self._status_dot = Gtk.Label(label="●", visible=True)
        self._status_dot.get_style_context().add_class("status-dot")
        self._status_text = Gtk.Label(xalign=0, visible=True)
        self._status_text.get_style_context().add_class("device-status-connected")
        self._battery_inline = Gtk.Label(xalign=1, visible=True)
        self._battery_inline.get_style_context().add_class("battery-indicator")
        status_bar.pack_start(self._status_dot, False, False, 0)
        status_bar.pack_start(self._status_text, True, True, 0)
        status_bar.pack_end(self._battery_inline, False, False, 0)
        self._content.pack_start(status_bar, False, False, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, visible=True)
        self._primary = self._action_tile("audio-volume-high-symbolic", _("Connect"), "primary-action-tile")
        self._send = self._action_tile("document-send-symbolic", _("Send File"), "action-tile")
        self._more = self._action_tile("view-more-symbolic", _("More"), "action-tile")
        for button, action in ((self._send, DeviceCardAction.SEND), (self._more, DeviceCardAction.MORE)):
            button.connect("clicked", self._request, action)
            actions.pack_start(button, True, True, 0)
        self._primary.connect("clicked", self._request_primary)
        actions.pack_start(self._primary, True, True, 0)
        self._content.pack_start(actions, False, False, 0)

        information = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, visible=True)
        information.get_style_context().add_class("inspector-section")
        info_title = Gtk.Label(label=_("Device Information"), xalign=0, visible=True)
        info_title.get_style_context().add_class("inspector-section-title")
        information.pack_start(info_title, False, False, 0)
        self._address = self._info_row(information, "bluetooth-symbolic", _("Address"))
        self._type = self._info_row(information, "phone-symbolic", _("Type"))
        self._status = self._info_row(information, "network-wireless-symbolic", _("Status"))
        self._battery = self._info_row(information, "battery-symbolic", _("Battery"))
        self._content.pack_start(information, False, False, 0)

        quick = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, visible=True)
        quick.get_style_context().add_class("inspector-section")
        quick_title = Gtk.Label(label=_("Quick Actions"), xalign=0, visible=True)
        quick_title.get_style_context().add_class("inspector-section-title")
        quick.pack_start(quick_title, False, False, 0)
        remove = Gtk.Button(visible=True)
        remove.get_style_context().add_class("quick-action-danger")
        remove.add(self._quick_action_content("edit-delete-symbolic", _("Forget Device")))
        remove.connect("clicked", self._request, DeviceCardAction.REMOVE)
        quick.pack_start(remove, False, False, 0)
        self._content.pack_start(quick, False, False, 0)
        self.pack_start(self._content, True, True, 0)

        self.device_list.connect("device-selected", self._on_selected)
        self.cards.connect("cards-changed", lambda _cards: self._refresh())
        selected = self.device_list.get_selected_device()
        if selected is not None:
            self._object_path = selected.get_object_path()
            self._refresh()

    @staticmethod
    def _action_tile(icon_name: str, label: str, css_class: str) -> Gtk.Button:
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=7, visible=True)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
        text = Gtk.Label(label=label, visible=True)
        button = Gtk.Button(visible=True)
        button._tile_label = text  # type: ignore[attr-defined]
        icon.show()
        content.pack_start(icon, False, False, 0)
        content.pack_start(text, False, False, 0)
        button.add(content)
        button.get_style_context().add_class(css_class)
        return button

    @staticmethod
    def _quick_action_content(icon_name: str, text: str) -> Gtk.Box:
        content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, visible=True)
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        label = Gtk.Label(label=text, xalign=0, visible=True)
        arrow = Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        icon.show()
        arrow.show()
        content.pack_start(icon, False, False, 0)
        content.pack_start(label, True, True, 0)
        content.pack_end(arrow, False, False, 0)
        return content

    @staticmethod
    def _info_row(parent: Gtk.Box, icon_name: str, label: str) -> Gtk.Label:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, visible=True)
        row.get_style_context().add_class("inspector-row")
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        key = Gtk.Label(label=label, xalign=0, visible=True)
        key.get_style_context().add_class("inspector-row-key")
        value = Gtk.Label(xalign=1, selectable=True, ellipsize=Pango.EllipsizeMode.END, visible=True)
        value.get_style_context().add_class("inspector-row-value")
        icon.show()
        row.pack_start(icon, False, False, 0)
        row.pack_start(key, True, True, 0)
        row.pack_end(value, False, False, 0)
        parent.pack_start(row, False, False, 0)
        return value

    def _on_selected(self, _list: object, device: Device | None, _tree_iter: object) -> None:
        self._object_path = device.get_object_path() if device is not None else None
        self._refresh()

    def _refresh(self) -> None:
        card = self.cards.cards_by_path.get(self._object_path or "")
        if card is None:
            self._empty.show()
            self._content.hide()
            return
        snapshot = card.snapshot
        self._empty.hide()
        self._content.show_all()
        self._icon.set_from_icon_name(snapshot.icon_name or "bluetooth", Gtk.IconSize.DIALOG)
        self._name.set_text(snapshot.name)
        self._name.set_tooltip_text(snapshot.name)
        self._category.set_text(snapshot.category)
        self._address.set_text(snapshot.address)
        self._type.set_text(snapshot.category)
        status = _("Connected") if snapshot.connected else _("Paired") if snapshot.paired else _("Available")
        self._status.set_text(status)
        self._status_text.set_text(status)
        status_context = self._status_text.get_style_context()
        dot_context = self._status_dot.get_style_context()
        for css_class in ("device-status-connected", "device-status-disconnected"):
            status_context.remove_class(css_class)
            dot_context.remove_class(css_class)
        state_class = "device-status-connected" if snapshot.connected else "device-status-disconnected"
        status_context.add_class(state_class)
        dot_context.add_class(state_class)
        battery = snapshot.battery_label
        self._battery.set_text(battery or _("Not reported"))
        self._battery_inline.set_text(("▰  " + battery) if battery else "")
        self._battery_inline.set_visible(battery is not None)
        primary_label = _("Disconnect") if snapshot.connected else _("Connect") if snapshot.paired else _("Pair")
        self._primary._tile_label.set_text(primary_label)  # type: ignore[attr-defined]
        self._send.set_visible(snapshot.can_send)

    def _request_primary(self, button: Gtk.Button) -> None:
        card = self.cards.cards_by_path.get(self._object_path or "")
        if card is None:
            return
        action = (
            DeviceCardAction.DISCONNECT if card.snapshot.connected
            else DeviceCardAction.CONNECT if card.snapshot.paired
            else DeviceCardAction.PAIR
        )
        self._request(button, action)

    def _request(self, button: Gtk.Button, action: DeviceCardAction) -> None:
        if self._object_path is not None:
            self.emit("action-requested", self._object_path, action.value, button)
