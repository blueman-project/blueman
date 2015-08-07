from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import wait_for_adapter, adapter_path_to_name, dprint

from blueman.main.SignalTracker import SignalTracker
from blueman.gui.GenericList import GenericList
from blueman.main.FakeDevice import FakeDevice
from blueman.main.Device import Device

from _blueman import conn_info
import blueman.bluez as Bluez

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject
import os
import re
import copy


class DeviceList(GenericList):
    __gsignals__ = {
        #@param: device TreeIter
        #note: None None is given when there ar no more rows, or when selected device is removed
        str('device-selected'): (
            GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)
        ),
        #@param: device, TreeIter, (key, value)
        #note: there is a special property "Fake", it's not a real property,
        #but it is used to notify when device changes state from "Fake" to a real BlueZ object
        #the callback would be called with Fake=False
        str('device-property-changed'): (
            GObject.SignalFlags.RUN_LAST,
            None,
            (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)
        ),
        #@param: adapter, (key, value)
        str('adapter-property-changed'): (
        GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
        #@param: progress (0 to 1)
        str('discovery-progress'): (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_FLOAT,)),

        #@param: new adapter path, None if there are no more adapters
        str('adapter-changed'): (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),

        #@param: adapter path
        str('adapter-added'): (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
        str('adapter-removed'): (GObject.SignalFlags.RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
    }

    def __del__(self):
        dprint("deleting mainlist")

    def __init__(self, adapter=None, tabledata=None):
        if not tabledata:
            tabledata = []

        def on_adapter_removed(path):
            self.emit("adapter-removed", path)
            if path == self.__adapter_path:
                self.clear()
                self.Adapter = None
                self.SetAdapter()

        def on_adapter_added(path):
            def on_activate():
                dprint("adapter powered", path)

                if self.Adapter is None:
                    self.SetAdapter(path)

                self.emit("adapter-added", path)

            a = Bluez.Adapter(path)
            wait_for_adapter(a, on_activate)

        #cache for fast lookup in the list
        self.address_to_row = {}
        self.path_to_row = {}

        self.monitored_devices = []

        self.signals = SignalTracker()

        self.manager = Bluez.Manager()
        self.signals.Handle(self.manager, on_adapter_removed, "AdapterRemoved")
        self.signals.Handle(self.manager, on_adapter_added, "AdapterAdded")

        self.__discovery_time = 0
        self.__adapter_path = None
        self.Adapter = None
        self.discovering = False

        data = []
        data = data + tabledata

        data = data + [
            ["device", object],
            ["dbus_path", str]
        ]

        GenericList.__init__(self, data)
        self.adapter_signals = SignalTracker()
        self.device_signals = SignalTracker()

        self.SetAdapter(adapter)

        self.signals.Handle(self.selection, "changed", self.on_selection_changed)

    def destroy(self):
        dprint("destroying")
        self.adapter_signals.DisconnectAll()
        self.device_signals.DisconnectAll()
        self.signals.DisconnectAll()
        self.device_signals = None
        #self.clear()
        if len(self.liststore):
            for i in self.liststore:
                iter = i.iter
                device = self.get(iter, "device")["device"]
            #device.Destroy()
        GenericList.destroy(self)

    def on_selection_changed(self, selection):
        iter = self.selected()
        if iter:
            row = self.get(iter, "device")
            dev = row["device"]
            self.emit("device-selected", dev, iter)

    def on_device_found(self, address, props):
        if self.discovering:
            dprint("Device discovered", address)

            props["Address"] = address
            props["Fake"] = True
            dev = FakeDevice(props)
            device = Device(dev)

            iter = self.find_device(dev)
            if not iter:
                self.device_add_event(device)
                iter = self.find_device(device)
                self.row_update_event(iter, "RSSI", props["RSSI"])
            else:
                self.row_update_event(iter, "Alias", props["Alias"])

            print("RSSI:", props["RSSI"])


    def on_property_changed(self, key, value):
        dprint("adapter propery changed", key, value)
        if key == "Discovering":
            if not value and self.discovering:
                self.StopDiscovery()

        self.emit("adapter-property-changed", self.Adapter, (key, value))

    def on_device_property_changed(self, key, value, path, *args, **kwargs):
        dprint("list: device_prop_ch", key, value, path)

        iter = self.find_device_by_path(path)

        if iter != None:
            dev = self.get(iter, "device")["device"]
            self.row_update_event(iter, key, value)

            self.emit("device-property-changed", dev, iter, (key, value))

            if key == "Connected":
                if value:
                    self.monitor_power_levels(dev)
                else:
                    r = Gtk.TreeRowReference.new(self.get_model(), self.props.model.get_path(iter))
                    self.level_setup_event(r, dev, None)

            elif key == "Paired":
                if value and dev.Temp:
                    dev.Temp = False

    def monitor_power_levels(self, device):
        def update(row_ref, cinfo, address):
            if not row_ref.valid():
                dprint("stopping monitor (row does not exist)")
                cinfo.deinit()
                self.monitored_devices.remove(props["Address"])
                return False

            if not self.get_model():
                self.monitored_devices.remove(props["Address"])
                return False

            iter = self.get_model().get_iter(row_ref.get_path())
            device = self.get(iter, "device")["device"]
            if not device.Valid or not device.Connected:
                dprint("stopping monitor (not connected)")
                cinfo.deinit()
                self.level_setup_event(row_ref, device, None)
                self.monitored_devices.remove(props["Address"])
                return False
            else:
                self.level_setup_event(row_ref, device, cinfo)
                return True


        props = device.get_properties()

        if "Connected" in props and props["Connected"] and props["Address"] not in self.monitored_devices:
            dprint("starting monitor")
            iter = self.find_device(device)

            hci = os.path.basename(self.Adapter.get_object_path())
            try:
                cinfo = conn_info(props["Address"], hci)
            except Exception as e:
                dprint("Failed to get power levels\n%s" % e)
            else:
                r = Gtk.TreeRowReference.new(self.get_model(), self.get_model().get_path(iter))
                self.level_setup_event(r, device, cinfo)
                GObject.timeout_add(1000, update, r, cinfo, props["Address"])
                self.monitored_devices.append(props["Address"])

    ##### virtual funcs #####

    #called when power levels need updating
    #if cinfo is None then info icons need to be removed
    def level_setup_event(self, iter, device, cinfo):
        pass

    #called when row needs to be initialized
    def row_setup_event(self, iter, device):
        pass

    #called when a property for a device changes
    def row_update_event(self, iter, key, value):
        pass

    #called when device needs to be added to the list
    #default action: append
    def device_add_event(self, device):
        self.AppendDevice(device)

    def device_remove_event(self, device, iter):
        self.RemoveDevice(device, iter)


    #########################

    def on_device_created(self, path):
        dprint("created", path)
        iter = self.find_device_by_path(path)
        if iter == None:
            dev = Bluez.Device(path)
            dev = Device(dev)
            dev.Temp = True
            self.device_add_event(dev)


    def on_device_removed(self, path):
        iter = self.find_device_by_path(path)
        if iter:
            row = self.get(iter, "device")
            dev = row["device"]

            self.device_remove_event(dev, iter)

    def SetAdapter(self, adapter=None):
        self.clear()
        if self.discovering:
            self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))
            self.StopDiscovery()

        if adapter is not None and adapter != "" and not re.match("hci[0-9]*", adapter):
            adapter = adapter_path_to_name(adapter)

        dprint(adapter)
        if self.Adapter is not None:
            self.adapter_signals.DisconnectAll()

        try:
            self.Adapter = self.manager.get_adapter(adapter)
            self.adapter_signals.Handle(self.Adapter, self.on_device_found, "DeviceFound")
            self.adapter_signals.Handle(self.Adapter, self.on_property_changed, "PropertyChanged")
            self.adapter_signals.Handle(self.Adapter, self.on_device_created, "DeviceCreated")
            self.adapter_signals.Handle(self.Adapter, self.on_device_removed, "DeviceRemoved")
            self.__adapter_path = self.Adapter.get_object_path()
            self.emit("adapter-changed", self.__adapter_path)
        except Bluez.errors.DBusNoSuchAdapterError as e:
            dprint(e)
            #try loading default adapter
            if len(self.manager.list_adapters()) > 0 and adapter is not None:
                self.SetAdapter()
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
            self.StopDiscovery()
            return False

        self.emit("discovery-progress", progress)
        return True

    def add_device(self, device, append=True):
        iter = self.find_device(device)
        #device belongs to another adapter
        if not device.Fake:
            if not device.get_object_path().startswith(self.Adapter.get_object_path()):
                return

        if iter == None:
            dprint("adding new device")
            if append:
                iter = self.liststore.append()
            else:
                iter = self.liststore.prepend()

            self.set(iter, device=device)
            self.row_setup_event(iter, device)

            props = device.get_properties()
            try:
                self.set(iter, dbus_path=device.get_object_path())
            except:
                pass

            if not "Fake" in props:
                self.device_signals.Handle("bluez", device,
                                           self.on_device_property_changed,
                                           "PropertyChanged",
                                           sigid=device.get_object_path(),
                                           path_keyword="path")
                if props["Connected"]:
                    self.monitor_power_levels(device)

        else:
            row = self.get(iter, "device")
            existing_dev = row["device"]

            props = existing_dev.get_properties()
            props_new = device.get_properties()

            #turn a Fake device to a Real device
            n = not "Fake" in props and not "Fake" in props_new
            if n:
                dprint("Updating existing dev")
                self.device_signals.Disconnect(existing_dev.get_object_path())
            #existing_dev.Destroy()

            if ("Fake" in props and not "Fake" in props_new) or n:
                self.set(iter, device=device, dbus_path=device.get_object_path())
                self.row_setup_event(iter, device)

                if not n:
                    self.emit("device-property-changed", device, iter, ("Fake", False))
                    self.row_update_event(iter, "Fake", False)

                self.device_signals.Handle("bluez", device,
                                           self.on_device_property_changed,
                                           "PropertyChanged",
                                           sigid=device.get_object_path(),
                                           path_keyword="path")

                if props_new["Connected"]:
                    self.monitor_power_levels(device)

            #turn a Real device to a Fake device
            elif not "Fake" in props and "Fake" in props_new:
                dprint("converting: real to discovered")
                self.set(iter, device=device, dbus_path=None)
                self.row_setup_event(iter, device)
                self.emit("device-property-changed", device, iter, ("Fake", True))
                self.row_update_event(iter, "Fake", True)

    def DisplayKnownDevices(self, autoselect=False):
        self.clear()
        devices = self.Adapter.list_devices()
        for device in devices:
            self.device_add_event(Device(device))

        if autoselect:
            self.selection.select_path(0)

    def DiscoverDevices(self, time=10.24):
        if not self.discovering:
            self.__discovery_time = 0
            if self.Adapter is not None:
                self.Adapter.start_discovery()
                self.discovering = True
                T = 1.0 / 15 * 1000
                GObject.timeout_add(int(T), self.update_progress, T / 1000, time)

    def IsValidAdapter(self):
        if self.Adapter == None:
            return False
        else:
            return True

    def GetAdapterPath(self):
        if self.IsValidAdapter():
            return self.__adapter_path

    def StopDiscovery(self):
        self.discovering = False
        if self.Adapter != None:
            self.Adapter.stop_discovery()

    def PrependDevice(self, device):
        self.add_device(device, False)

    def AppendDevice(self, device):
        self.add_device(device, True)

    def RemoveDevice(self, device, iter=None):
        dprint(device)
        if iter == None:
            iter = self.find_device(device)

        if not device.Temp and self.compare(self.selected(), iter):
            self.emit("device-selected", None, None)

        try:
            props = device.get_properties()
        except:
            self.device_signals.Disconnect(device.get_object_path())
        else:
            if not "Fake" in props:
                self.device_signals.Disconnect(device.get_object_path())

        self.delete(iter)

    def GetSelectedDevice(self):
        selected = self.selected()
        if selected != None:
            row = self.get(selected, "device")
            device = row["device"]
            return device

    def clear(self):
        if len(self.liststore):
            for i in self.liststore:
                iter = i.iter
                device = self.get(iter, "device")["device"]
                self.RemoveDevice(device, iter)
            self.liststore.clear()
            self.emit("device-selected", None, None)

        self.address_to_row = {}
        self.path_to_row = {}

    def find_device(self, device):
        if type(device) == str:
            address = device
        else:
            address = device.Address

        try:
            row = self.address_to_row[address]
            if row.valid():
                path = row.get_path()
                iter = self.get_model().get_iter(path)
                return iter
            else:
                del self.address_to_row[address]
                return None

        except KeyError:
            return None

    def find_device_by_path(self, path):
        try:
            row = self.path_to_row[path]
            if row.valid():
                path = row.get_path()
                iter = self.get_model().get_iter(path)
                return iter
            else:
                del self.path_to_row[path]
                return None
        except KeyError:
            return None

    def do_cache(self, iter, kwargs):
        if "device" in kwargs:
            if kwargs["device"]:
                self.address_to_row[kwargs["device"].Address] = Gtk.TreeRowReference.new(self.get_model(),
                                                                                         self.get_model().get_path(iter))
                dprint("Caching new device %s" % kwargs["device"].Address)

        if "dbus_path" in kwargs:
            if kwargs["dbus_path"] != None:
                self.path_to_row[kwargs["dbus_path"]] = Gtk.TreeRowReference.new(self.get_model(),
                                                                                 self.get_model().get_path(iter))
            else:
                existing = self.get(iter, "dbus_path")["dbus_path"]
                if existing != None:
                    del self.path_to_row[existing]

    def append(self, **columns):
        iter = GenericList.append(self, **columns)
        self.do_cache(iter, columns)

    def prepend(self, **columns):
        iter = GenericList.prepend(self, **columns)
        self.do_cache(iter, columns)

    def set(self, iter, **kwargs):
        self.do_cache(iter, kwargs)
        GenericList.set(self, iter, **kwargs)
