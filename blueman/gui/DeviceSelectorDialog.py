from gettext import gettext as _
from typing import Any, cast, Optional, Tuple
import logging

from blueman.bluez.Device import Device
from blueman.Functions import adapter_path_to_name
from blueman.bluemantyping import ObjectPath
from blueman.main.Builder import Builder

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk


class DeviceRow(Gtk.ListBoxRow):
    def __init__(
            self,
            device_path: ObjectPath,
            adapter_path: ObjectPath,
            device_icon: str = "blueman",
            alias: str = _("Unnamed device"),
            warning: bool = False
    ) -> None:
        super().__init__(visible=True)

        self.adapter_path = adapter_path
        self.device_path = device_path

        builder = Builder("sendto-rowbox.ui")
        box = builder.get_widget("row_box", Gtk.Box)
        self.add(box)

        self._row_icon = builder.get_widget("row_icon", Gtk.Image)
        self._row_alias_label = builder.get_widget("row_alias", Gtk.Label)
        self._row_warning = builder.get_widget("row_warn", Gtk.Image)

        row_adapter_label = builder.get_widget("row_adapter_name", Gtk.Label)
        adapter_name = adapter_path_to_name(adapter_path)
        assert adapter_name is not None
        row_adapter_label.set_markup(f"<i>({adapter_name})</i>")

        self.device_icon_name = device_icon
        self.description = alias
        self.warning = warning

    @property
    def device_icon_name(self) -> str:
        return self._row_icon.get_icon_name()[0]

    @device_icon_name.setter
    def device_icon_name(self, icon_name: str) -> None:
        self._row_icon.set_from_icon_name(icon_name, size=Gtk.IconSize.SMALL_TOOLBAR)

    @property
    def description(self) -> str:
        return self._row_alias_label.get_label()

    @description.setter
    def description(self, text: str) -> None:
        self._row_alias_label.set_label(text)

    @property
    def warning(self) -> bool:
        return self._row_warning.get_visible()

    @warning.setter
    def warning(self, warning: bool) -> None:
        self._row_warning.set_visible(warning)


class DeviceSelector:
    selection: Optional[Tuple[ObjectPath, Optional[Device]]]

    def __init__(self, adapter_name: str = "any") -> None:
        self._rows: dict[ObjectPath, DeviceRow] = {}
        self._default_adapter_name = adapter_name
        builder = Builder("sendto-device-dialog.ui")
        self.dialog = builder.get_widget("select_device_dialog", Gtk.Dialog)
        self._adapter_combo = builder.get_widget("adapter_combo", Gtk.ComboBoxText)

        self._discover_spinner = builder.get_widget("discover_toggle_spinner", Gtk.Spinner)

        self._listbox = builder.get_widget("device_listbox", Gtk.ListBox)
        self._listbox.set_filter_func(self.__list_filter_func, None)
        self._listbox.connect("row-selected", self.__on_row_selected)
        self._listbox.connect("button-press-event", self.__on_button_press)

        self._adapter_combo.connect("changed", lambda _: self._listbox.invalidate_filter())

    def add_adapter(self, object_path: ObjectPath) -> None:
        name = adapter_path_to_name(object_path)
        if name is None:
            raise ValueError("Invalid adapter")
        pos = int(name[-1]) + 1
        self._adapter_combo.insert(pos, name, name)
        if name == self._default_adapter_name:
            self._adapter_combo.set_active_id(name)

    def remove_adapter(self, object_path: ObjectPath) -> None:
        name = adapter_path_to_name(object_path)
        if name is None:
            raise ValueError("Invalid adapter")

        for key in self._rows:
            if self._rows[key].adapter_path == object_path:
                row = self._rows.pop(key)
                self._listbox.remove(row)

        if name == self._adapter_combo.get_active_id():
            self._adapter_combo.set_active_id("any")

        pos = int(name[-1]) + 1
        self._adapter_combo.remove(pos)

    def add_device(self, object_path: ObjectPath, show_warning: bool) -> None:
        device = Device(obj_path=object_path)
        row = DeviceRow(
            device_path=object_path,
            adapter_path=device["Adapter"],
            device_icon=f"{device['Icon']}-symbolic",
            alias=device.display_name,
            warning=show_warning
        )

        self._listbox.add(row)
        self._rows[object_path] = row

    def remove_device(self, object_path: ObjectPath) -> None:
        row = self._rows.pop(object_path)
        self._listbox.remove(row)

    def update_row(self, object_path: ObjectPath, element: str, value: Any) -> None:
        row = self._rows.get(object_path, None)
        if row is None:
            raise ValueError(f"Unknown device {object_path}")

        match element:
            case "description":
                row.description = value
            case "warning":
                row.warning = value

    def set_discovering(self, discovering: bool) -> None:
        if discovering:
            self._discover_spinner.start()
        else:
            self._discover_spinner.stop()

    def __list_filter_func(self, row: Gtk.ListBoxRow, _: Any) -> bool:
        row = cast(DeviceRow, row)
        active_id = self._adapter_combo.get_active_id()
        adapter_name = adapter_path_to_name(row.adapter_path)
        if active_id == "any" or active_id == adapter_name:
            return True
        else:
            return False

    def __on_row_selected(self, _listbox: Gtk.ListBox, row: Gtk.ListBoxRow | None) -> None:
        if row is None:
            self.__select_first_row()
            return

        row = cast(DeviceRow, row)
        logging.debug(f"{row.device_path}")
        device = Device(obj_path=row.device_path)
        self.selection = row.adapter_path, device

    def __on_button_press(self, _listbox: Gtk.ListBox, event: Gdk.EventButton) -> bool:
        if event.type == Gdk.EventType._2BUTTON_PRESS:
            self.dialog.response(Gtk.ResponseType.ACCEPT)
            return True
        return False

    def __select_first_row(self) -> None:
        for row in self._listbox.get_children():
            row = cast(DeviceRow, row)
            if row.get_selectable():
                self._listbox.select_row(row)

    def __cleanup(self) -> None:
        self._listbox.destroy()
        self.dialog.destroy()
        del self._listbox
        del self.dialog

    def run(self) -> int:
        return self.dialog.run()

    def close(self) -> None:
        self.dialog.close()
        self.__cleanup()
