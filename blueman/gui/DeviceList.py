from datetime import datetime
import os
import logging
from typing import Dict, List, Optional, Any, Callable

from blueman.Functions import adapter_path_to_name
from blueman.gui.GenericList import GenericList, ListDataDict
from blueman.Constants import ICON_PATH
from _blueman import conn_info, ConnInfoReadError
from blueman.bluez.Manager import Manager
from blueman.bluez.Device import Device, AnyDevice
from blueman.bluez.Adapter import Adapter, AnyAdapter
from blueman.bluez.errors import DBusNoSuchAdapterError, BluezDBusException

from gi.repository import GObject
from gi.repository import GLib

import gi

from blueman.typing import GSignals

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

    def __init__(self, adapter_name: Optional[str] = None, tabledata: Optional[List[ListDataDict]] = None,
                 **kwargs: object) -> None:
        if not tabledata:
            tabledata = []

        # cache for fast lookup in the list
        self.path_to_row: Dict[str, Gtk.TreeRowReference] = {}

        self.monitored_devices: List[str] = []

        self.manager = Manager()
        self._managerhandlers: List[int] = []
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
        self.__adapter_path: Optional[str] = None
        self.Adapter: Optional[Adapter] = None
        self.discovering = False

        data = tabledata + [
            {"id": "device", "type": object},
            {"id": "dbus_path", "type": str},
            {"id": "timestamp", "type": float}
        ]

        super().__init__(data, **kwargs)
        self.set_name("DeviceList")

        self.set_adapter(adapter_name)
        self._any_adapter = AnyAdapter()
        self._anyadapterhandler = self._any_adapter.connect_signal("property-changed", self._on_property_changed)

        self._selectionhandler = self.selection.connect('changed', self.on_selection_changed)

        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path(ICON_PATH)
        # handle icon theme changes
        self.icon_theme.connect("changed", self.on_icon_theme_changed)

    def destroy(self) -> None:
        self.any_device.disconnect(self._anydevhandler)
        self._any_adapter.disconnect(self._anyadapterhandler)
        self.selection.disconnect(self._selectionhandler)
        for handler in self._managerhandlers:
            self.manager.disconnect(handler)
        super().destroy()

    def __on_manager_signal(self, _manager: Manager, path: str, signal_name: str) -> None:
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
            tree_iter = self.find_device_by_path(path)
            if tree_iter is None:
                dev = Device(obj_path=path)
                self.device_add_event(dev)

        if signal_name == 'device-removed':
            tree_iter = self.find_device_by_path(path)
            if tree_iter:
                row = self.get(tree_iter, "device")
                dev = row["device"]

                self.device_remove_event(dev)

    def on_selection_changed(self, selection: Gtk.TreeSelection) -> None:
        _model, tree_iter = selection.get_selected()
        if tree_iter:
            row = self.get(tree_iter, "device")
            dev = row["device"]
            self.emit("device-selected", dev, tree_iter)

    def _on_property_changed(self, _adapter: AnyAdapter, key: str, value: object, path: str) -> None:
        if not self.Adapter or self.Adapter.get_object_path() != path:
            return

        if key == "Discovering":
            if not value and self.discovering:
                self.stop_discovery()

        self.emit("adapter-property-changed", self.Adapter, (key, value))

    def _on_device_property_changed(self, _device: AnyDevice, key: str, value: object, path: str) -> None:
        tree_iter = self.find_device_by_path(path)

        if tree_iter is not None:
            dev = self.get(tree_iter, "device")["device"]
            self.row_update_event(tree_iter, key, value)

            self.emit("device-property-changed", dev, tree_iter, (key, value))

            if key == "Connected":
                if value:
                    self.monitor_power_levels(dev)
                else:
                    r = Gtk.TreeRowReference.new(self.get_model(), self.props.model.get_path(tree_iter))
                    self.level_setup_event(r, dev, None)

    # Override when subclassing
    def on_icon_theme_changed(self, _icon_them: Gtk.IconTheme) -> None:
        logging.warning("Icons may not be updated with icon theme changes")

    def monitor_power_levels(self, device: Device) -> None:
        def update(row_ref: Gtk.TreeRowReference, cinfo: conn_info, address: str) -> bool:
            if not row_ref.valid():
                logging.warning("stopping monitor (row does not exist)")
                cinfo.deinit()
                self.monitored_devices.remove(address)
                return False

            if not self.get_model():
                self.monitored_devices.remove(address)
                return False

            if not device['Connected']:
                logging.info("stopping monitor (not connected)")
                cinfo.deinit()
                self.level_setup_event(row_ref, device, None)
                self.monitored_devices.remove(address)
                return False
            else:
                self.level_setup_event(row_ref, device, cinfo)
                return True

        bt_address = device["Address"]
        if device["Connected"] and bt_address not in self.monitored_devices:
            logging.info("starting monitor")
            tree_iter = self.find_device(device)

            assert self.Adapter is not None
            hci = os.path.basename(self.Adapter.get_object_path())
            cinfo = conn_info(bt_address, hci)
            try:
                cinfo.init()
            except ConnInfoReadError:
                logging.warning("Failed to get power levels, probably a LE device.")

            r = Gtk.TreeRowReference.new(self.get_model(), self.get_model().get_path(tree_iter))
            self.level_setup_event(r, device, cinfo)
            GLib.timeout_add(1000, update, r, cinfo, bt_address)
            self.monitored_devices.append(bt_address)

    # ##### virtual funcs #####

    # called when power levels need updating
    # if cinfo is None then info icons need to be removed
    def level_setup_event(self, row_ref: Gtk.TreeRowReference, device: Device, cinfo: Optional[conn_info]) -> None:
        pass

    # called when row needs to be initialized
    def row_setup_event(self, tree_iter: Gtk.TreeIter, device: Device) -> None:
        pass

    # called when a property for a device changes
    def row_update_event(self, tree_iter: Gtk.TreeIter, key: str, value: Any) -> None:
        pass

    # called when device needs to be added to the list
    def device_add_event(self, device: Device) -> None:
        self.add_device(device)

    def device_remove_event(self, device: Device) -> None:
        logging.debug(device)
        tree_iter = self.find_device(device)

        if self.compare(self.selected(), tree_iter):
            self.emit("device-selected", None, None)

        self.delete(tree_iter)

    #########################

    def set_adapter(self, adapter: Optional[str] = None) -> None:
        self.clear()
        if self.discovering:
            self.stop_discovery()
            self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))

        adapter = adapter_path_to_name(adapter)

        logging.debug(f"Setting adapter to: {adapter}")

        if adapter is not None:
            try:
                self.Adapter = self.manager.get_adapter(adapter)
                self.__adapter_path = self.Adapter.get_object_path()
            except DBusNoSuchAdapterError:
                logging.warning('Failed to set adapter, trying first available.')
                self.set_adapter(None)
                return
        else:
            adapters = self.manager.get_adapters()
            if len(adapters) > 0:
                self.Adapter = adapters[0]
                self.__adapter_path = self.Adapter.get_object_path()
            else:
                self.Adapter = None
                self.__adapter_path = None

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

    def add_device(self, device: Device) -> None:
        # device belongs to another adapter
        if not self.Adapter or not device['Adapter'] == self.Adapter.get_object_path():
            return

        logging.info("adding new device")
        tree_iter = self.liststore.append()

        self.set(tree_iter, device=device)
        self.row_setup_event(tree_iter, device)

        object_path = device.get_object_path()
        timestamp = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')
        self.set(tree_iter, dbus_path=object_path, timestamp=float(timestamp))

        if device["Connected"]:
            self.monitor_power_levels(device)

    def display_known_devices(self, autoselect: bool = False) -> None:
        self.clear()
        if self.Adapter:
            devices = self.manager.get_devices(self.Adapter.get_object_path())
            for device in devices:
                self.device_add_event(device)

        if autoselect:
            self.selection.select_path(0)

    def discover_devices(self, time: float = 10.24,
                         error_handler: Optional[Callable[[BluezDBusException], None]] = None) -> None:
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

    def get_adapter_path(self) -> Optional[str]:
        return self.__adapter_path if self.is_valid_adapter() else None

    def stop_discovery(self) -> None:
        self.discovering = False
        if self.Adapter is not None:
            self.Adapter.stop_discovery()

    def get_selected_device(self) -> Optional[Device]:
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
                device = self.get(tree_iter, "device")["device"]
                self.device_remove_event(device)
            self.liststore.clear()
            self.emit("device-selected", None, None)

        self.path_to_row = {}

    def find_device(self, device: Device) -> Optional[Gtk.TreeIter]:
        object_path = device.get_object_path()
        try:
            row = self.path_to_row[object_path]
            if row.valid():
                path = row.get_path()
                tree_iter = self.liststore.get_iter(path)
                return tree_iter
            else:
                del self.path_to_row[object_path]
                return None

        except KeyError:
            return None

    def find_device_by_path(self, path: str) -> Optional[Gtk.TreeIter]:
        try:
            row = self.path_to_row[path]
            if row.valid():
                path = row.get_path()
                tree_iter = self.liststore.get_iter(path)
                return tree_iter
            else:
                del self.path_to_row[path]
                return None
        except KeyError:
            return None

    def do_cache(self, tree_iter: Gtk.TreeIter, kwargs: Dict[str, Any]) -> None:
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

    def append(self, **columns: object) -> None:
        tree_iter = GenericList.append(self, **columns)
        self.do_cache(tree_iter, columns)

    def prepend(self, **columns: object) -> None:
        tree_iter = GenericList.prepend(self, **columns)
        self.do_cache(tree_iter, columns)

    def set(self, iterid: Gtk.TreeIter, **kwargs: object) -> None:
        GenericList.set(self, iterid, **kwargs)
        self.do_cache(iterid, kwargs)
