# coding=utf-8
from datetime import datetime
import os
import re
import logging

from blueman.Functions import wait_for_adapter, adapter_path_to_name
from blueman.gui.GenericList import GenericList
from blueman.Constants import ICON_PATH
from _blueman import conn_info, ConnInfoReadError
import blueman.bluez as bluez

from gi.repository import GObject
from gi.repository import GLib

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class DeviceList(GenericList):
    __gsignals__ = {
        # @param: device TreeIter
        # note: None None is given when there ar no more rows, or when selected device is removed
        'device-selected': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        # @param: device, TreeIter, (key, value)
        'device-property-changed': (GObject.SignalFlags.RUN_LAST, None,
                                    (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        # @param: adapter, (key, value)
        'adapter-property-changed': (GObject.SignalFlags.RUN_LAST, None,
                                     (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        # @param: progress (0 to 1)
        'discovery-progress': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_FLOAT,)),

        # @param: new adapter path, None if there are no more adapters
        'adapter-changed': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),

        # @param: adapter path
        'adapter-added': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
        'adapter-removed': (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __del__(self):
        logging.debug("deleting mainlist")

    def __init__(self, adapter_name=None, tabledata=None, **kwargs):
        if not tabledata:
            tabledata = []

        def on_adapter_removed(_manager, path):
            self.emit("adapter-removed", path)
            if path == self.__adapter_path:
                self.clear()
                self.Adapter = None
                self.set_adapter()

        def on_adapter_added(_manager, path):
            def on_activate():
                logging.info("adapter powered %s" % path)

                if self.Adapter is None:
                    self.set_adapter(path)

                self.emit("adapter-added", path)

            a = bluez.Adapter(path)
            wait_for_adapter(a, on_activate)

        # cache for fast lookup in the list
        self.path_to_row = {}

        self.monitored_devices = []

        self.manager = bluez.Manager()
        self.manager.connect_signal('adapter-removed', on_adapter_removed)
        self.manager.connect_signal('adapter-added', on_adapter_added)

        any_device = bluez.AnyDevice()
        any_device.connect_signal("property-changed", self._on_device_property_changed)

        self.__discovery_time = 0
        self.__adapter_path = None
        self.Adapter = None
        self.discovering = False

        data = tabledata + [
            {"id": "device", "type": object},
            {"id": "dbus_path", "type": str},
            {"id": "timestamp", "type": float}
        ]

        super(DeviceList, self).__init__(data, **kwargs)
        self.set_name("DeviceList")

        self.set_adapter(adapter_name)
        self._any_adapter = bluez.AnyAdapter()
        self._any_adapter.connect_signal("property-changed", self._on_property_changed)

        self.selection.connect('changed', self.on_selection_changed)

        self.icon_theme = Gtk.IconTheme.get_default()
        self.icon_theme.prepend_search_path(ICON_PATH)
        # handle icon theme changes
        self.icon_theme.connect("changed", self.on_icon_theme_changed)

    def on_selection_changed(self, selection):
        _model, tree_iter = selection.get_selected()
        if tree_iter:
            row = self.get(tree_iter, "device")
            dev = row["device"]
            self.emit("device-selected", dev, tree_iter)

    def _on_property_changed(self, _adapter, key, value, path):
        if self.Adapter.get_object_path() != path:
            return

        if key == "Discovering":
            if not value and self.discovering:
                self.stop_discovery()

        self.emit("adapter-property-changed", self.Adapter, (key, value))

    def _on_device_property_changed(self, _device, key, value, path):
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
    def on_icon_theme_changed(self, widget):
        logging.warning("Icons may not be updated with icon theme changes")

    def monitor_power_levels(self, device):
        def update(row_ref, cinfo, address):
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

            hci = os.path.basename(self.Adapter.get_object_path())
            try:
                cinfo = conn_info(bt_address, hci)
            except ConnInfoReadError:
                logging.warning("Failed to get power levels", exc_info=True)
            else:
                r = Gtk.TreeRowReference.new(self.get_model(), self.get_model().get_path(tree_iter))
                self.level_setup_event(r, device, cinfo)
                GLib.timeout_add(1000, update, r, cinfo, bt_address)
                self.monitored_devices.append(bt_address)

    # ##### virtual funcs #####

    # called when power levels need updating
    # if cinfo is None then info icons need to be removed
    def level_setup_event(self, tree_iter, device, cinfo):
        pass

    # called when row needs to be initialized
    def row_setup_event(self, tree_iter, device):
        pass

    # called when a property for a device changes
    def row_update_event(self, tree_iter, key, value):
        pass

    # called when device needs to be added to the list
    def device_add_event(self, device):
        self.add_device(device)

    def device_remove_event(self, device, tree_iter):
        logging.debug(device)
        if tree_iter is None:
            tree_iter = self.find_device(device)

        if self.compare(self.selected(), tree_iter):
            self.emit("device-selected", None, None)

        self.delete(tree_iter)

    #########################

    def _on_device_created(self, _adapter, path):
        tree_iter = self.find_device_by_path(path)
        if tree_iter is None:
            dev = bluez.Device(path)
            self.device_add_event(dev)

    def _on_device_removed(self, _manager, path):
        tree_iter = self.find_device_by_path(path)
        if tree_iter:
            row = self.get(tree_iter, "device")
            dev = row["device"]

            self.device_remove_event(dev, tree_iter)

    def set_adapter(self, adapter=None):
        self.clear()
        if self.discovering:
            self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))
            self.stop_discovery()

        if adapter is not None and adapter != "" and not re.match("hci[0-9]*", adapter):
            adapter = adapter_path_to_name(adapter)

        logging.debug(adapter)

        try:
            self.Adapter = self.manager.get_adapter(adapter)
            # The patern may be incorrect (ie removed adapter), see #590
            if self.Adapter is None:
                self.Adapter = self.manager.get_adapter()

            self.manager.connect_signal('device-created', self._on_device_created)
            self.manager.connect_signal('device-removed', self._on_device_removed)
            self.__adapter_path = self.Adapter.get_object_path()
            self.emit("adapter-changed", self.__adapter_path)
        except bluez.errors.DBusNoSuchAdapterError as e:
            logging.exception(e)
            # try loading default adapter
            if len(self.manager.get_adapters()) > 0 and adapter is not None:
                self.set_adapter()
            else:
                self.Adapter = None
                self.emit("adapter-changed", None)

    def update_progress(self, time, totaltime):
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

    def add_device(self, device):
        # device belongs to another adapter
        if not device['Adapter'] == self.Adapter.get_object_path():
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

    def display_known_devices(self, autoselect=False):
        self.clear()
        devices = self.manager.get_devices(self.Adapter.get_object_path())
        for device in devices:
            self.device_add_event(device)

        if autoselect:
            self.selection.select_path(0)

    def discover_devices(self, time=10.24):
        if not self.discovering:
            self.__discovery_time = 0
            if self.Adapter is not None:
                self.Adapter.start_discovery()
                self.discovering = True
                t = 1.0 / 15 * 1000
                GLib.timeout_add(int(t), self.update_progress, t / 1000, time)

    def is_valid_adapter(self):
        if self.Adapter is None:
            return False
        else:
            return True

    def get_adapter_path(self):
        if self.is_valid_adapter():
            return self.__adapter_path

    def stop_discovery(self):
        self.discovering = False
        if self.Adapter is not None:
            self.Adapter.stop_discovery()

    def get_selected_device(self):
        selected = self.selected()
        if selected is not None:
            row = self.get(selected, "device")
            device = row["device"]
            return device

    def clear(self):
        if len(self.liststore):
            for i in self.liststore:
                tree_iter = i.iter
                device = self.get(tree_iter, "device")["device"]
                self.device_remove_event(device, tree_iter)
            self.liststore.clear()
            self.emit("device-selected", None, None)

        self.path_to_row = {}

    def find_device(self, device):
        object_path = device.get_object_path()
        try:
            row = self.path_to_row[object_path]
            if row.valid():
                path = row.get_path()
                tree_iter = self.get_model().get_iter(path)
                return tree_iter
            else:
                del self.path_to_row[object_path]
                return None

        except KeyError:
            return None

    def find_device_by_path(self, path):
        try:
            row = self.path_to_row[path]
            if row.valid():
                path = row.get_path()
                tree_iter = self.get_model().get_iter(path)
                return tree_iter
            else:
                del self.path_to_row[path]
                return None
        except KeyError:
            return None

    def do_cache(self, tree_iter, kwargs):
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
            logging.info("Caching new device %s" % object_path)
            self.path_to_row[object_path] = Gtk.TreeRowReference.new(self.get_model(),
                                                                     self.get_model().get_path(tree_iter))

    def append(self, **columns):
        tree_iter = GenericList.append(self, **columns)
        self.do_cache(tree_iter, columns)

    def prepend(self, **columns):
        tree_iter = GenericList.prepend(self, **columns)
        self.do_cache(tree_iter, columns)

    def set(self, tree_iter, **kwargs):
        GenericList.set(self, tree_iter, **kwargs)
        self.do_cache(tree_iter, kwargs)
