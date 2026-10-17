"""Selection-bound device inspector for the redesigned manager."""

from gettext import gettext as _

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk, Pango  # noqa: E402

from blueman.bluez.Device import Device
from blueman.gui.manager.ManagerDeviceCards import DeviceCardAction, DeviceCardSnapshot, ManagerDeviceCards


class ManagerDeviceInspector(Gtk.Box):
    __gsignals__ = {
        "action-requested": (GObject.SignalFlags.RUN_LAST, None, (str, str, object)),
    }

    def __init__(self, cards: ManagerDeviceCards) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16, margin=20, width_request=340, visible=True)
        self.cards = cards
        self.device_list = cards.device_list
        self._object_path: str | None = None
        self.get_style_context().add_class("inspector-panel")

        self._empty = Gtk.Label(label=_("Select a device to view details"), wrap=True, visible=True)
        self._empty.get_style_context().add_class("inspector-subtitle")
        self.pack_start(self._empty, True, True, 0)

        self._content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self._icon = Gtk.Image(pixel_size=72, visible=True)
        self._name = Gtk.Label(xalign=0, ellipsize=Pango.EllipsizeMode.END, visible=True)
        self._name.get_style_context().add_class("inspector-title")
        self._category = Gtk.Label(xalign=0, visible=True)
        self._category.get_style_context().add_class("inspector-subtitle")
        self._content.pack_start(self._icon, False, False, 0)
        self._content.pack_start(self._name, False, False, 0)
        self._content.pack_start(self._category, False, False, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        self._primary = Gtk.Button(visible=True)
        self._primary.get_style_context().add_class("primary-button")
        self._send = Gtk.Button(label=_("Send File"), visible=True)
        self._send.get_style_context().add_class("secondary-button")
        self._more = Gtk.Button(label=_("More"), visible=True)
        self._more.get_style_context().add_class("secondary-button")
        for button, action in ((self._send, DeviceCardAction.SEND), (self._more, DeviceCardAction.MORE)):
            button.connect("clicked", self._request, action)
            actions.pack_start(button, True, True, 0)
        self._primary.connect("clicked", self._request_primary)
        actions.pack_start(self._primary, True, True, 0)
        self._content.pack_start(actions, False, False, 0)

        self._address = self._info_row(_("Address"))
        self._status = self._info_row(_("Status"))
        self._battery = self._info_row(_("Battery"))

        rename = Gtk.Button(label=_("Rename Device"), visible=True)
        rename.get_style_context().add_class("secondary-button")
        rename.connect("clicked", self._request, DeviceCardAction.RENAME)
        remove = Gtk.Button(label=_("Forget Device"), visible=True)
        remove.get_style_context().add_class("danger-button")
        remove.connect("clicked", self._request, DeviceCardAction.REMOVE)
        self._content.pack_end(remove, False, False, 0)
        self._content.pack_end(rename, False, False, 0)
        self.pack_start(self._content, True, True, 0)

        self.device_list.connect("device-selected", self._on_selected)
        self.cards.connect("cards-changed", lambda _cards: self._refresh())

    def _info_row(self, label: str) -> Gtk.Label:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, visible=True)
        key = Gtk.Label(label=label, xalign=0, visible=True)
        key.get_style_context().add_class("inspector-row-key")
        value = Gtk.Label(xalign=1, selectable=True, visible=True)
        value.get_style_context().add_class("inspector-row-value")
        row.pack_start(key, True, True, 0)
        row.pack_end(value, False, False, 0)
        self._content.pack_start(row, False, False, 0)
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
        self._category.set_text(snapshot.category)
        self._address.set_text(snapshot.address)
        status = _("Connected") if snapshot.connected else _("Paired") if snapshot.paired else _("Available")
        self._status.set_text(status)
        self._battery.set_text(snapshot.battery_label or _("Not reported"))
        primary_label = _("Disconnect") if snapshot.connected else _("Connect") if snapshot.paired else _("Pair")
        self._primary.set_label(primary_label)
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
