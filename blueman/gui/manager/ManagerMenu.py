import logging
from typing import TYPE_CHECKING, Any
from collections.abc import Sequence
from blueman.bluemantyping import ObjectPath

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.bluez.Manager import Manager
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList
from blueman.gui.manager.ManagerDeviceMenu import ManagerDeviceMenu
from blueman.Functions import adapter_path_to_name

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerMenu:
    def __init__(self, blueman: "Blueman"):
        self.blueman = blueman
        self.Config = Gio.Settings(schema_id="org.blueman.general")

        self.adapter_items: dict[str, tuple[Gtk.RadioMenuItem, Adapter]] = {}
        self._adapters_group: Sequence[Gtk.RadioMenuItem] = []
        self._insert_adapter_item_pos = 2

        self.item_adapter = self.blueman.builder.get_widget("item_adapter", Gtk.MenuItem)
        self.item_device = self.blueman.builder.get_widget("item_device", Gtk.MenuItem)

        self.device_menu: ManagerDeviceMenu | None = None

        self._sort_alias_item = blueman.builder.get_widget("sort_name_item", Gtk.CheckMenuItem)
        self._sort_timestamp_item = blueman.builder.get_widget("sort_added_item", Gtk.CheckMenuItem)

        sort_config = self.Config['sort-by']
        if sort_config == "alias":
            self._sort_alias_item.props.active = True
        else:
            self._sort_timestamp_item.props.active = True

        self.Search = blueman.builder.get_widget("search_item", Gtk.ImageMenuItem)

        self._adapter_settings = blueman.builder.get_widget("prefs_item", Gtk.ImageMenuItem)

        self._manager = Manager()
        self._manager.connect_signal("adapter-added", self.on_adapter_added)
        self._manager.connect_signal("adapter-removed", self.on_adapter_removed)

        blueman.List.connect("device-selected", self.on_device_selected)

        for adapter in self._manager.get_adapters():
            self.on_adapter_added(None, adapter.get_object_path())

        self.Config.connect("changed", self._on_settings_changed)
        self._sort_alias_item.connect("activate", self._on_sorting_changed, "alias")
        self._sort_timestamp_item.connect("activate", self._on_sorting_changed, "timestamp")

    def _on_sorting_changed(self, _btn: Gtk.CheckMenuItem, sort_opt: str) -> None:
        action = self.blueman.lookup_action("sort-by")
        assert action is not None
        action.change_state(GLib.Variant.new_string(sort_opt))

    def _on_settings_changed(self, settings: Gio.Settings, key: str) -> None:
        value = settings[key]
        if key == 'sort-by':
            if value == "alias":
                if not self._sort_alias_item.props.active:
                    self._sort_alias_item.props.active = True
            elif value == "timestamp":
                if not self._sort_timestamp_item.props.active:
                    self._sort_timestamp_item.props.active = True
        elif key == "hide-unnamed":
            logging.debug("refilter")
            self.blueman.List.filter.refilter()
        elif key == "show-toolbar":
            toolbar = self.blueman.builder.get_widget("toolbar", Gtk.Toolbar)
            toolbar.set_visible(value)
        elif key == "show-statusbar":
            statusbar = self.blueman.builder.get_widget("statusbar", Gtk.Box)
            statusbar.set_visible(value)

    def on_device_selected(self, _lst: ManagerDeviceList, device: Device | None, tree_iter: Gtk.TreeIter) -> None:
        if tree_iter and device:
            self.item_device.props.sensitive = True

            if self.device_menu is None:
                self.device_menu = ManagerDeviceMenu(self.blueman)
                self.item_device.set_submenu(self.device_menu)
            else:
                def idle() -> bool:
                    assert self.device_menu is not None  # https://github.com/python/mypy/issues/2608
                    self.device_menu.generate()
                    return False
                GLib.idle_add(idle, priority=GLib.PRIORITY_LOW)

        else:
            self.item_device.props.sensitive = False

    def on_adapter_property_changed(self, _adapter: Adapter, name: str, value: Any, path: str) -> None:
        if name == "Name" or name == "Alias":
            item = self.adapter_items[path][0]
            item.set_label(value)
        elif name == "Discovering":
            if self.Search:
                if value:
                    self.Search.props.sensitive = False
                else:
                    self.Search.props.sensitive = True
        elif name == "Powered":
            self._update_power()

    def on_adapter_selected(self, menuitem: Gtk.CheckMenuItem, adapter_path: str) -> None:
        if menuitem.props.active:
            assert self.blueman.List.Adapter is not None
            if adapter_path != self.blueman.List.Adapter.get_object_path():
                logging.info(f"selected {adapter_path}")
                self.blueman.Config["last-adapter"] = adapter_path_to_name(adapter_path)
                self.blueman.List.set_adapter(adapter_path)

    def on_adapter_added(self, _manager: Manager | None, adapter_path: ObjectPath) -> None:
        adapter = Adapter(obj_path=adapter_path)
        menu = self.item_adapter.get_submenu()
        assert isinstance(menu, Gtk.Menu)

        item = Gtk.RadioMenuItem.new_with_label(self._adapters_group, adapter.get_name())
        item.show()
        self._adapters_group = item.get_group()

        self._itemhandler = item.connect("activate", self.on_adapter_selected, adapter_path)
        self._adapterhandler = adapter.connect_signal("property-changed", self.on_adapter_property_changed)

        menu.insert(item, self._insert_adapter_item_pos)
        self._insert_adapter_item_pos += 1

        self.adapter_items[adapter_path] = (item, adapter)

        assert self.blueman.List.Adapter is not None
        if adapter_path == self.blueman.List.Adapter.get_object_path():
            item.props.active = True

        self._update_power()

    def on_adapter_removed(self, _manager: Manager, adapter_path: str) -> None:
        item, adapter = self.adapter_items.pop(adapter_path)
        menu = self.item_adapter.get_submenu()
        assert isinstance(menu, Gtk.Menu)

        item.disconnect(self._itemhandler)
        adapter.disconnect(self._adapterhandler)

        menu.remove(item)
        self._insert_adapter_item_pos -= 1

        self._update_power()

    def _update_power(self) -> None:
        if self.device_menu is not None:
            self.device_menu.generate()

        if any(adapter["Powered"] for (_, adapter) in self.adapter_items.values()):
            self.Search.props.visible = True
            self._adapter_settings.props.visible = True
        else:
            self.Search.props.visible = False
            self._adapter_settings.props.visible = False
