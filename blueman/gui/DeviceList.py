from datetime import datetime
import logging
from typing import Any
from collections.abc import Callable

from blueman.Functions import adapter_path_to_name
from blueman.gui.GenericList import GenericList, ListDataDict
from blueman.Constants import ICON_PATH
from blueman.bluez.Manager import Manager
from blueman.bluez.Device import Device, AnyDevice
from blueman.bluez.Adapter import Adapter, AnyAdapter
from blueman.bluez.errors import BluezDBusException

from gi.repository import GObject
from gi.repository import GLib

import gi

from blueman.bluemantyping import GSignals, ObjectPath

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceList(GenericList):
    __gsignals__: GSignals = {
        # @param: device TreeIter
        # note: None None is given when there ar no more rows, or when selected device is removed
        'device-selected': (GObject.SignalFlags.RUN_LAST, None, (Device, Gtk.TreeIter,)),
        # @param: device, TreeIter, (key, value)
        'device-property-changed': (GObject.SignalFlags.RUN_LAST, None, (Device, Gtk.TreeIter, object,)),
        # @param: adapter, (key, value)
        'adapter-property-changed': (GObject.SignalFlags.RUN_LAST, None, (Adapter, object,)),
        # @param: progress (0 to 1)
        'discovery-progress': (GObject.SignalFlags.RUN_LAST, None, (float,)),

        # @param: new adapter path, None if there are no more adapters
        'adapter-changed': (GObject.SignalFlags.RUN_LAST, None, (str,)),

        # @param: adapter path
        'adapter-added': (GObject.SignalFlags.RUN_LAST, None, (str,)),
        'adapter-removed': (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }

    def __init__(self, adapter_name: str | None = None, tabledata: list[ListDataDict] | None = None,
                 headers_visible: bool = True) -> None:
        if not tabledata:
            tabledata = []

        # cache for fast lookup in the list
        self.path_to_row: dict[str, Gtk.TreeRowReference] = {}

        self.manager = Manager()
        self._managerhandlers: list[int] = []
        self._managerhandlers.append(self.manager.connect_signal('adapter-removed', self.__on_manager_signal,
                                                                 'adapter-removed'))
        self._managerhandlers.append(self.manager.connect_signal('adapter-added', self.__on_manager_signal,
                                                                 'adapter-added'))
        self._managerhandlers.append(self.manager.connect_signal('device-created', self.__on_manager_signal,
                                                                 'device-created'))
        self._managerhandlers.append(self.manager.connect_signal('device-removed', self.__on_manager_signal,
                                                                 'device-removed'))

        self.any_device = AnyDevice()
        self._anydevhandler = self.any_device.connect_signal("property-changed", self._on_device_property_changed)

        self.__discovery_time: float = 0
        self.__adapter_path: ObjectPath | None = None
        self.Adapter: Adapter | None = None
        self.discovering = False

        data = tabledata + [
            {"id": "device", "type": object},
            {"id": "dbus_path", "type": str},
            {"id": "timestamp", "type": float},
            {"id": "no_name", "type": bool}
        ]

        super().__init__(data, headers_visible=headers_visible)
        self.set_name("DeviceList")

        self.set_adapter(adapter_name)
        self._any_adapter = AnyAdapter()
        self._anyadapterhandler = self._any_adapter.connect_signal("property-changed", self._on_property_changed)

        self._selectionhandler = self.selection.connect('changed', self.on_selection_changed)

        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path(ICON_PATH.as_posix())
        # handle icon theme changes
        self.icon_theme.connect("changed", self.on_icon_theme_changed)

    def destroy(self) -> None:
        self.any_device.disconnect(self._anydevhandler)
        self._any_adapter.disconnect(self._anyadapterhandler)
        self.selection.disconnect(self._selectionhandler)
        for handler in self._managerhandlers:
            self.manager.disconnect(handler)
        super().destroy()

    def __on_manager_signal(self, _manager: Manager, path: ObjectPath, signal_name: str) -> None:
        if signal_name == 'adapter-removed':
            self.emit("adapter-removed", path)
            if path == self.__adapter_path:
                self.clear()
                self.Adapter = None
                self.set_adapter()

        if signal_name == 'adapter-added':
            if self.Adapter is None:
                self.set_adapter(path)

            self.emit("adapter-added", path)

        if signal_name == 'device-created':
            self.device_add_event(path)

        if signal_name == 'device-removed':
            self.device_remove_event(path)

    def on_selection_changed(self, selection: Gtk.TreeSelection) -> None:
        model, tree_iter = selection.get_selected()
        if tree_iter:
            tree_iter = model.convert_iter_to_child_iter(tree_iter)
            row = self.get(tree_iter, "device")
            dev = row["device"]
            self.emit("device-selected", dev, tree_iter)

    def _on_property_changed(self, _adapter: AnyAdapter, key: str, value: object, path: ObjectPath) -> None:
        if not self.Adapter or self.Adapter.get_object_path() != path:
            return

        if key == "Discovering" and not value:
            self.discovering = False

        self.emit("adapter-property-changed", self.Adapter, (key, value))

    def _on_device_property_changed(self, _device: AnyDevice, key: str, value: object, path: ObjectPath) -> None:
        tree_iter = self.find_device_by_path(path)

        if tree_iter is not None:
            dev = self.get(tree_iter, "device")["device"]
            self.row_update_event(tree_iter, key, value)

            self.emit("device-property-changed", dev, tree_iter, (key, value))

    # Override when subclassing
    def on_icon_theme_changed(self, _icon_them: Gtk.IconTheme) -> None:
        logging.warning("Icons may not be updated with icon theme changes")

    # ##### virtual funcs #####

    # called when row needs to be initialized
    def row_setup_event(self, tree_iter: Gtk.TreeIter, device: Device) -> None:
        pass

    # called when a property for a device changes
    def row_update_event(self, tree_iter: Gtk.TreeIter, key: str, value: Any) -> None:
        pass

    # called when device needs to be added to the list
    def device_add_event(self, object_path: ObjectPath) -> None:
        self.add_device(object_path)

    def device_remove_event(self, object_path: ObjectPath) -> None:
        logging.debug(object_path)
        tree_iter = self.find_device_by_path(object_path)
        if tree_iter is None:
            return

        if self.compare(self.selected(), tree_iter):
            self.emit("device-selected", None, None)

        self.delete(tree_iter)
        del self.path_to_row[object_path]

    #########################

    def set_adapter(self, adapter: ObjectPath | str | None = None) -> None:
        self.clear()
        if self.discovering:
            self.stop_discovery()
            self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))

        adapter = adapter_path_to_name(adapter)
        adapter_path: ObjectPath | None = None
        emit_signal: bool = False

        if adapter is not None:
            adapter_path = self.manager.find_adapter(adapter)
            if adapter_path is None:
                logging.warning(f'Failed to find adapter {adapter}, trying first available.')

        if adapter_path is None:
            # Try and find any adapter
            adapter_path = self.manager.find_adapter(None)

        if adapter_path is not None:
            logging.debug(f"Setting adapter to: {adapter_path_to_name(adapter_path)}")
            emit_signal = adapter_path != self.__adapter_path
            self.Adapter = Adapter(obj_path=adapter_path)
            self.__adapter_path = adapter_path

        if emit_signal:
            self.emit("adapter-changed", self.__adapter_path)

    def update_progress(self, time: float, totaltime: float) -> bool:
        if not self.discovering:
            return False

        self.__discovery_time += time

        progress = self.__discovery_time / totaltime
        if progress >= 1.0:
            progress = 1.0
        if self.__discovery_time >= totaltime:
            self.stop_discovery()
            return False

        self.emit("discovery-progress", progress)
        return True

    def add_device(self, object_path: ObjectPath) -> None:
        device = Device(obj_path=object_path)
        # device belongs to another adapter
        if not self.Adapter or not device['Adapter'] == self.Adapter.get_object_path():
            return

        logging.info("adding new device")

        colls = {
            "device": device,
            "dbus_path": object_path,
            "timestamp": float(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')),
            "no_name": "Name" not in device
        }

        tree_iter = self.append(**colls)
        self.row_setup_event(tree_iter, device)

        if self.get_selected_device() is None:
            self.selection.select_path(Gtk.TreePath.new_first())

    def populate_devices(self) -> None:
        self.clear()
        self.manager.populate_devices()

    def discover_devices(self, time: float = 60.0,
                         error_handler: Callable[[BluezDBusException], None] | None = None) -> None:
        if not self.discovering:
            self.__discovery_time = 0
            if self.Adapter is not None:
                self.Adapter.start_discovery(error_handler=error_handler)
                self.discovering = True
                t = 1.0 / 15 * 1000
                GLib.timeout_add(int(t), self.update_progress, t / 1000, time)

    def is_valid_adapter(self) -> bool:
        if self.Adapter is None:
            return False
        else:
            return True

    def get_adapter_path(self) -> ObjectPath | None:
        return self.__adapter_path if self.is_valid_adapter() else None

    def stop_discovery(self) -> None:
        self.discovering = False
        if self.Adapter is not None:
            self.Adapter.stop_discovery()

    def get_selected_device(self) -> Device | None:
        selected = self.selected()
        if selected is not None:
            row = self.get(selected, "device")
            device: Device = row["device"]
            return device
        return None

    def clear(self) -> None:
        if len(self.liststore):
            for i in self.liststore:
                tree_iter = i.iter
                dbus_path = self.get(tree_iter, "dbus_path")["dbus_path"]
                self.device_remove_event(dbus_path)
            self.liststore.clear()
            self.emit("device-selected", None, None)

        self.path_to_row = {}

    def find_device_by_path(self, object_path: ObjectPath) -> Gtk.TreeIter | None:
        row = self.path_to_row.get(object_path, None)
        if row is None:
            return row

        if row.valid():
            tree_path = row.get_path()
            assert tree_path is not None
            tree_iter = self.liststore.get_iter(tree_path)
            return tree_iter
        else:
            del self.path_to_row[object_path]
            return None

    def do_cache(self, tree_iter: Gtk.TreeIter, kwargs: dict[str, Any]) -> None:
        object_path = None

        if "device" in kwargs:
            if kwargs["device"]:
                object_path = kwargs['device'].get_object_path()

        elif "dbus_path" in kwargs:
            if kwargs["dbus_path"]:
                object_path = kwargs['dbus_path']
            else:
                existing = self.get(tree_iter, "dbus_path")["dbus_path"]
                if existing is not None:
                    del self.path_to_row[existing]

        if object_path:
            logging.info(f"Caching new device {object_path}")
            self.path_to_row[object_path] = Gtk.TreeRowReference.new(self.liststore,
                                                                     self.liststore.get_path(tree_iter))

    def append(self, **list_columns: object) -> Gtk.TreeIter:
        tree_iter = super().append(**list_columns)
        self.do_cache(tree_iter, list_columns)
        return tree_iter

    def prepend(self, **list_columns: object) -> Gtk.TreeIter:
        tree_iter = super().prepend(**list_columns)
        self.do_cache(tree_iter, list_columns)
        return tree_iter

    def set(self, tree_iter: Gtk.TreeIter, **kwargs: object) -> None:
        super().set(tree_iter, **kwargs)
        self.do_cache(tree_iter, kwargs)
