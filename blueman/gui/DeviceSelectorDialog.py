from gettext import gettext as _
from typing import Any, Optional, Tuple
import logging

from blueman.bluez.Device import Device, AnyDevice
from blueman.bluez.Manager import Manager
from blueman.Functions import adapter_path_to_name
from blueman.bluemantyping import ObjectPath
from blueman.main.Builder import Builder

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceRow(Gtk.ListBoxRow):
    def __init__(
            self,
            device_path: ObjectPath,
            adapter_path: ObjectPath = "/org/bluez/hci0",
            device_icon: str = "blueman",
            alias: str = _("Unnamed device"),
            paired: bool = False,
            trusted: bool = False
        ) -> None:
        super().__init__()

        self.adapter_path = adapter_path
        self.device_path = device_path
        builder = Builder("sendto-rowbox.ui")
        self.__box = builder.get_widget("row_box", Gtk.Box)
        self._device_icon = builder.get_widget("row_icon", Gtk.Image)
        self._row_label = builder.get_widget("row_label", Gtk.Label)
        self._row_paired = builder.get_widget("revealer_paired", Gtk.Revealer)
        self._row_trusted = builder.get_widget("revealer_trusted", Gtk.Revealer)

        self.add(self.__box)

        self.device_icon_name = device_icon
        self.row_description = f"{alias} ({adapter_path_to_name(adapter_path)})"
        self.paired = paired
        self.trusted = trusted

    @property
    def device_icon_name(self) -> str:
        return self._device_icon.get_icon_name()

    @device_icon_name.setter
    def device_icon_name(self, icon_name: str) -> None:
        self._device_icon.set_from_icon_name(icon_name, size=Gtk.IconSize.SMALL_TOOLBAR)

    @property
    def row_description(self) -> str:
        return self._row_label.get_label()

    @row_description.setter
    def row_description(self, text: str) -> None:
        self._row_label.set_label(text)

    @property
    def paired(self) -> bool:
        return self._row_paired.get_reveal_child()

    @paired.setter
    def paired(self, paired: bool) -> None:
        self._row_paired.set_reveal_child(paired)

    @property
    def trusted(self) -> bool:
        return self._row_trusted.get_reveal_child()

    @trusted.setter
    def trusted(self, trusted: bool):
        self._row_trusted.set_reveal_child(trusted)


class DeviceSelector:
    selection: Optional[Tuple[ObjectPath, Optional[ObjectPath]]]

    def __init__(self, discover: bool = True, adapter_name: str = "any") -> None:
        self._rows: dict[ObjectPath, DeviceRow] = {}
        builder = Builder("sendto-device-dialog.ui")
        self.dialog = builder.get_widget("select_device_dialog", Gtk.Dialog)
        self._adapter_combo = builder.get_widget("adapter_combo", Gtk.ComboBox)

        self._listbox = builder.get_widget("device_listbox", Gtk.ListBox)
        self._listbox.set_filter_func(self.__list_filter_func)
        self._listbox.connect("row-selected", self.__on_row_selected)

        self._manager = Manager()
        self.__any_device = AnyDevice()

        adapter_names = sorted([adapter_path_to_name(a.get_object_path()) for a in self._manager.get_adapters()])
        for name in adapter_names:
            pos = int(name[-1]) + 1
            self._adapter_combo.insert(pos, name, name)

        self._adapter_combo.connect("changed", lambda _: self._listbox.invalidate_filter())
        if adapter_name in adapter_names:
            self._adapter_combo.set_active_id(adapter_name)
        else:
            logging.debug(adapter_names)
            logging.debug(adapter_name)
            logging.warning(f"Adapter {adapter_name} not found!")

        self._manager.connect_signal("adapter-added", self.__on_manager_signal, "adapter-added")
        self._manager.connect_signal("adapter-removed", self.__on_manager_signal, "adapter-removed")
        self._manager.connect_signal("device-created", self.__on_manager_signal, "device-added")
        self._manager.connect_signal("device-removed", self.__on_manager_signal, "device-removed")

        self.__any_device.connect_signal("property-changed", self.__on_device_property_changed)

        self._manager.populate_devices()

    def __list_filter_func(self, row: Gtk.ListBoxRow) -> bool:
        active_id = self._adapter_combo.get_active_id()
        adapter_name = adapter_path_to_name(row.adapter_path)
        if active_id == "any" or active_id == adapter_name:
            return True
        else:
            return False

    def __on_manager_signal(self, _manager: Manager, object_path: ObjectPath, signal_name: str):
        logging.debug(f"{object_path} {signal_name}")
        match signal_name:
            case "adapter-added":
                adapter_name = adapter_path_to_name(object_path)
                pos = int(adapter_name[-1]) + 1
                self._adapter_combo.insert(pos, adapter_name, adapter_name)
                self._manager.populate_devices(adapter_path=object_path)
            case "adapter-removed":
                for key in self._rows:
                    if self._rows[key].adapter_path == object_path:
                        row = self._rows.pop(key)
                        self._listbox.remove(row)

                adapter_name = adapter_path_to_name(object_path)
                if adapter_name == self._adapter_combo.set_active_id:
                    self._adapter_combo.set_active_id(adapter_name)

                pos = int(adapter_name[-1]) + 1
                self._adapter_combo.remove(pos)

            case "device-added":
                props = Device(obj_path=object_path).get_properties()
                row = DeviceRow(object_path, props["Adapter"], props["Icon"], props['Alias'], props["Paired"], props["Trusted"])
                row.show_all()
                self._listbox.add(row)
                self._rows[object_path] = row
            case "device-removed":
                row = self._rows.pop(object_path)
                self._listbox.remove(row)
            case _:
                raise ValueError(f"Unhandled signal {signal_name}")

    def __on_device_property_changed(self, _device: AnyDevice, key: str, value: Any, object_path: ObjectPath) -> None:
        row = self._rows.get(object_path, None)
        if row is None:
            return

        match key:
            case "Trusted":
                row.trusted = value
            case "Paired":
                row.paired = value

    def __on_row_selected(self, _listbox, row):
        logging.debug(f"{row.device_path}")
        device = Device(obj_path=row.device_path)
        self.selection = row.adapter_path, device

    def run(self) -> int:
        return self.dialog.run()

    def close(self) -> None:
        # FIXME implement a destroy method self.selector.destroy()
        self.dialog.close()
