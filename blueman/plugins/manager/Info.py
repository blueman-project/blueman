from collections.abc import Callable
from gettext import gettext as _
from typing import Any
from blueman.bluemantyping import ObjectPath
from gi.repository import Gtk, Gdk, Gio, GObject

import json
import logging

from blueman.Functions import create_menuitem
from blueman.Sdp import ServiceUUID
from blueman.bluez.Device import Device, AnyDevice
from blueman.bluez.errors import BluezDBusException
from blueman.gui.manager.ManagerDeviceMenu import MenuItemsProvider, ManagerDeviceMenu, DeviceMenuItem
from blueman.main.Builder import Builder

from blueman.plugins.ManagerPlugin import ManagerPlugin

DevicePropertyTypes = str | int | bool | list[str]
PropertyDataType = dict[str, str | list[str]]


def format_advflags(flags: list[int]) -> str:
    return ", ".join([str(flag) for flag in flags])


def format_boolean(x: bool) -> str:
    return _('yes') if x else _('no')


def format_rssi(rssi: int) -> str:
    if rssi in (0x99, 0x7f):
        return f'invalid (0x{rssi:02x})'
    else:
        return f'{rssi} dBm (0x{rssi:02x})'


def format_class(cls: int) -> str:
    return f"0x{cls:06x}"


def format_appearance(appearance: int) -> str:
    return f"0x{appearance:04x}"


def data_to_plain_text(data: PropertyDataType, values_only: bool) -> str:
    lines = []
    for prop, value in data.items():
        if isinstance(value, list):
            line = ", ".join(value)
        else:
            line = value

        if not values_only:
            lines.append(f"{prop}, {line}")
        else:
            lines.append(line)

    return "\n".join(lines)


def data_to_json(data: PropertyDataType, values_only: bool) -> str:
    return json.dumps(data)


# Property name and position in the list
Properties: dict[str, tuple[int, Callable[[Any], str]]] = {
    "Address": (10, str),
    "AddressType": (20, str),
    "Name": (30, str),
    "Alias": (40, str),
    "Class": (50, format_class),
    "Appearance": (60, format_appearance),
    "Icon": (70, str),
    "Paired": (80, format_boolean),
    "Bonded": (90, format_boolean),
    "Trusted": (100, format_boolean),
    "Blocked": (110, format_boolean),
    "LegacyPairing": (120, format_boolean),
    "RSSI": (130, format_rssi),
    "TxPower": (140, str),
    "Connected": (150, format_boolean),
    "UUIDs": (160, str),
    "Modalias": (170, str),
    "Adapter": (180, str),
    "ManufacturerData": (190, str),
    "ServiceData": (200, str),
    "AdvertisingData": (210, format_advflags),
    "ServicesResolved": (220, format_boolean),
    "WakeAllowed": (230, format_boolean),
    "PreferredBearer": (240, str),
    "CablePairing": (250, format_boolean)
}


class InfoItem(GObject.Object):
    __gtype_name__ = "InfoItem"

    class _Props:
        object_path: ObjectPath
        property_name: str
        position: int
        description: str
        value: str
        max_width: int

    props: _Props

    object_path = GObject.Property(type=str)
    property_name = GObject.Property(type=str)
    position = GObject.Property(type=int)
    description = GObject.Property(type=str)
    value = GObject.Property(type=str)
    max_width = GObject.Property(type=int, default=0)

    def __init__(
            self,
            object_path: ObjectPath,
            property_name: str,
            position: int,
            description: str,
            value: str
    ) -> None:
        super().__init__()
        self.props.object_path = object_path
        self.props.property_name = property_name
        self.props.position = position
        self.props.description = description
        self.props.value = value


class InfoWindow(Gtk.ApplicationWindow):
    def __init__(self, title: str, object_path: ObjectPath, application: Gtk.Application) -> None:
        super().__init__(title=title, icon_name="blueman", application=application)
        self._object_path = object_path
        self.__clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.__items: dict[str, InfoItem] = {}
        self.__format: str = "plain"
        self.__values_only: bool = True

        self.__model = Gio.ListStore.new(InfoItem.__gtype__)
        self.__model.connect("items-changed", self.__on_items_changed)

        builder = Builder("manager-info.ui")
        self.add(builder.get_widget("info_grid", Gtk.Grid))
        self.__listbox = builder.get_widget("info_listbox", Gtk.ListBox)
        self.__listbox.bind_model(self.__model, self.__widget_factory)

        cb_format = builder.get_widget("cb_format", Gtk.ComboBoxText)
        cb_format.set_active_id(self.__format)
        cb_format.connect("changed", self.__on_combo_changed)

        bt_values_only = builder.get_widget("bt_values_only", Gtk.CheckButton)
        bt_values_only.set_active(self.__values_only)
        bt_values_only.connect("toggled", self.__on_values_only_toggled)

        bt_copy = builder.get_widget("bt_copy", Gtk.Button)
        bt_copy.connect("clicked", self.__on_copy_clicked)

        accelgroup = Gtk.AccelGroup()
        self.add_accel_group(accelgroup)

        key, mod = Gtk.accelerator_parse("<Control>C")
        accelgroup.connect(key, mod, Gtk.AccelFlags.MASK, self.__on_accel_activated)

    def find_item(self, description: str) -> InfoItem | None:
        """Find InfoItem in the model and return it."""
        return self.__items.get(description, None)

    def add_item(self, item: InfoItem) -> None:
        """Insert InfoItem into the model"""
        self.__items[item.props.description] = item
        self.__model.insert_sorted(item, self.__model_sort_func)

    def remove_item(self, item: InfoItem) -> None:
        """Remove InfoItem from the model"""
        found, position = self.__model.find(item)
        if found is None:
            logging.error(f"Item not found {item}")
            return

        self.__model.remove(position)
        del self.__items[item.props.description]

    def remove_item_by_prop(self, property_name: str) -> None:
        """Removes all items of the same property name."""
        item_descriptions = list(self.__items.keys())
        for description in item_descriptions:
            item = self.__items[description]
            found, position = self.__model.find(item)
            if found and item.props.property_name == property_name:
                self.__model.remove(position)
                del self.__items[description]

    def copy_to_clipboard(self) -> None:
        positions = [r.get_index() for r in self.__listbox.get_selected_rows()]
        d = self.__build_data_dict(positions)

        match self.__format:
            case "plain":
                data_formatter = data_to_plain_text
            case "json":
                data_formatter = data_to_json
            case _:
                logging.error(f"Unknown format {self.__format}, using plain")
                data_formatter = data_to_plain_text

        text = data_formatter(d, self.__values_only)
        self.__clipboard.set_text(text, -1)

    def __build_data_dict(self, positions: list[int]) -> PropertyDataType:
        data_dict: PropertyDataType = {}
        for pos in positions:
            item = self.__model.get_item(pos)
            if item is None:
                continue

            assert isinstance(item, InfoItem)
            name = item.props.property_name
            if name == "UUIDs":
                dict_entry = data_dict.setdefault(name, [])
                assert isinstance(dict_entry, list)
                dict_entry.append(item.props.value)
            else:
                data_dict[name] = item.props.value

        return data_dict

    def __on_accel_activated(
            self,
            _group: Gtk.AccelGroup,
            _gobject: GObject.Object,
            key: int,
            _modifier: Gdk.ModifierType
    ) -> bool:
        if key != 99:
            logging.warning(f"Ignoring key {key}")
            return False

        self.copy_to_clipboard()

        return True

    def __on_combo_changed(self, combobox: Gtk.ComboBoxText) -> None:
        fmt = combobox.get_active_id()
        if fmt is None:
            return
        self.__format = fmt

    def __on_values_only_toggled(self, button: Gtk.CheckButton) -> None:
        self.__values_only = button.get_active()

    def __on_copy_clicked(self, _button: Gtk.Button) -> None:
        self.copy_to_clipboard()

    def destroy(self) -> None:
        """Remove model, widgets and other objects from Window."""
        self.__model.remove_all()
        self.__listbox.destroy()

        del self.__model
        del self.__listbox
        del self.__items

        super().destroy()

    def __on_items_changed(self, _model: Gio.ListStore, _position: int, _removed: int, _added: int) -> None:
        max_length = 0
        for item in self.__model:
            if item is None:
                continue
            assert isinstance(item, InfoItem)
            description_length = len(item.props.description)
            if description_length > max_length:
                max_length = description_length

        for item in self.__model:
            assert isinstance(item, InfoItem)
            item.props.max_width = max_length

    def __model_sort_func(self, item1: object | None, item2: object | None, _data: object | None = None) -> int:
        assert isinstance(item1, InfoItem)
        assert isinstance(item2, InfoItem)
        if item1.props.position < item2.props.position:
            return -1
        elif item1.props.position > item2.props.position:
            return 1
        else:
            return 0

    def __widget_factory(self, item: GObject.Object, _data: object | None = None) -> Gtk.Widget:
        """Factory function creating the widgets for the ListBox"""
        assert isinstance(item, InfoItem)
        box = Gtk.Box(spacing=3, margin=2, visible=True)
        prop_label = Gtk.Label(xalign=0, visible=True)
        value_label = Gtk.Label(visible=True)
        item.bind_property("description", prop_label, "label", GObject.BindingFlags.SYNC_CREATE)
        item.bind_property("value", value_label, "label", GObject.BindingFlags.SYNC_CREATE)
        item.bind_property("max_width", prop_label, "width_chars", GObject.BindingFlags.SYNC_CREATE)
        box.add(prop_label)
        box.add(value_label)
        return box


class Info(ManagerPlugin, MenuItemsProvider):
    _windows: dict[ObjectPath, InfoWindow] = {}
    _any_device: AnyDevice

    def on_load(self) -> None:
        self._any_device = AnyDevice()
        self._any_device.connect_signal("property-changed", self.__update_item)

    def on_unload(self) -> None:
        del self._any_device

    def create_item(self, property_name: str, object_path: ObjectPath, value: DevicePropertyTypes) -> InfoItem:
        description, item_value = self.format_property(property_name, value)

        item = InfoItem(
            object_path=object_path,
            property_name=property_name,
            position=Properties[property_name][0],
            description=description,
            value=item_value
        )
        return item

    def __update_item(self, _proxy: AnyDevice, prop: str, value: DevicePropertyTypes, object_path: ObjectPath) -> None:
        logging.debug(f"Updating {prop} for {object_path}")
        if object_path not in self._windows:
            return

        if prop not in Properties:
            logging.info(f"Skipping {prop}")
            return

        info_window = self._windows.get(object_path, None)
        if info_window is None:
            return

        # Simplest is to remove all UUID items and recreate them
        if prop == "UUIDs":
            info_window.remove_item_by_prop(prop)

        item = info_window.find_item(prop)
        if item is not None and value is None:
            info_window.remove_item(item)
            return

        if item is None:
            item = self.create_item(
                property_name=prop,
                object_path=object_path,
                value=value
            )
            info_window.add_item(item)
        else:
            prop_label, value_label = self.format_property(prop, value)
            item.props.description = prop_label
            item.props.value = value_label

    def format_property(self, property_name: str, value: DevicePropertyTypes) -> tuple[str, str]:
        _position, formatter = Properties[property_name]
        if property_name == "UUIDs":
            assert isinstance(value, str)
            return f"UUID ({ServiceUUID(value).name})", formatter(value)
        else:
            return property_name, formatter(value)

    def _show_info(self, _menuitem: Gtk.MenuItem, device: Device) -> None:
        object_path = device.get_object_path()

        window = self._windows.get(object_path, None)
        if window is not None:
            window.present()
            return

        title = f"{device['Alias']} ({device['Address']})"
        window = InfoWindow(title, object_path, self.parent)
        window.connect("delete-event", self.__on_window_delete)
        self._windows[object_path] = window

        for prop in Properties:
            # 0 is a property fallback added by blueman, skip it as it's not worth showing
            if prop in ("Class", "Appearance") and device[prop] == 0:
                continue

            try:
                value = device[prop]
            except BluezDBusException:
                logging.info(f"Property {prop} not available for device {device['Alias']}")
                continue

            if prop == "UUIDs":
                for uuid in value:
                    item = self.create_item(
                        object_path=object_path,
                        property_name=prop,
                        value=uuid,
                    )
                    window.add_item(item)

            else:
                item = self.create_item(
                    object_path=object_path,
                    property_name=prop,
                    value=value
                )
                window.add_item(item)

        window.present()

    def __on_window_delete(self, window: InfoWindow, _event: Gdk.Event) -> bool:
        logging.debug(window._object_path)
        window.destroy()
        del self._windows[window._object_path]
        return False

    def on_request_menu_items(
        self,
        manager_menu: ManagerDeviceMenu,
        device: Device,
        _powered: bool,
    ) -> list[DeviceMenuItem]:
        item = create_menuitem(_("_Info"), "dialog-information-symbolic")
        item.props.tooltip_text = _("Show device information")
        item.connect('activate', self._show_info, device)
        return [DeviceMenuItem(item, DeviceMenuItem.Group.ACTIONS, 400)]
