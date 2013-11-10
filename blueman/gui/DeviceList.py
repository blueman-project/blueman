from blueman.Functions import wait_for_adapter, adapter_path_to_name, dprint

from blueman.main.SignalTracker import SignalTracker
from blueman.gui.GenericList import GenericList
from blueman.main.FakeDevice import FakeDevice
from blueman.main.Device import Device

from blueman.Lib import conn_info
import blueman.bluez as Bluez
import gtk
import gobject
import os
import re
import copy


class DeviceList(GenericList):
    __gsignals__ = {
        #@param: device
        'device-found': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        #@param: device TreeIter
        #note: None None is given when there ar no more rows, or when selected device is removed
        'device-selected': (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)
        ),
        #@param: device, TreeIter, (key, value)
        #note: there is a special property "Fake", it's not a real property,
        #but it is used to notify when device changes state from "Fake" to a real BlueZ object
        #the callback would be called with Fake=False
        'device-property-changed': (
            gobject.SIGNAL_RUN_LAST,
            gobject.TYPE_NONE,
            (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)
        ),
        #@param: adapter, (key, value)
        'adapter-property-changed': (
        gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
        #@param: progress (0 to 1)
        'discovery-progress': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),

        #@param: new adapter path, None if there are no more adapters
        'adapter-changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),

        #@param: adapter path
        'adapter-added': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
        'adapter-removed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
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
        self.discovered_devices = []

        self.signals = SignalTracker()

        try:
            self.Manager = Bluez.Manager("gobject")
            self.signals.Handle(self.Manager, on_adapter_removed, "AdapterRemoved")
            self.signals.Handle(self.Manager, on_adapter_added, "AdapterAdded")
        except:
            self.Manager = None

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

            if not address in self.discovered_devices:
                self.emit("device-found", device)
                self.discovered_devices.append(address)

            iter = self.find_device(dev)
            if not iter:
                self.device_add_event(device)
                iter = self.find_device(device)
                self.row_update_event(iter, "RSSI", props["RSSI"])
            else:
                self.row_update_event(iter, "Alias", props["Alias"])

            print "RSSI:", props["RSSI"]


    def on_property_changed(self, key, value):
        dprint("adapter propery changed", key, value)
        if key == "Discovering":
            if not value and self.discovering:
                self.StopDiscovery()

            self.discovered_devices = []

        self.emit("adapter-property-changed", self.Adapter, (key, value))

    def on_device_property_changed(self, key, value, path, *args, **kwargs):
        dprint("list: device_prop_ch", key, value, path, args, kwargs)

        iter = self.find_device_by_path(path)

        if iter != None:
            dev = self.get(iter, "device")["device"]
            self.row_update_event(iter, key, value)

            self.emit("device-property-changed", dev, iter, (key, value))

            if key == "Connected":
                if value:
                    self.monitor_power_levels(dev)
                else:
                    r = gtk.TreeRowReference(self.props.model, self.props.model.get_path(iter))
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

            if not self.props.model:
                self.monitored_devices.remove(props["Address"])
                return False

            iter = self.props.model.get_iter(row_ref.get_path())
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


        props = device.GetProperties()

        if "Connected" in props and props["Connected"] and props["Address"] not in self.monitored_devices:
            dprint("starting monitor")
            iter = self.find_device(device)

            hci = os.path.basename(self.Adapter.GetObjectPath())
            try:
                cinfo = conn_info(props["Address"], hci)
            except:
                dprint("Failed to get power levels")
            else:
                r = gtk.TreeRowReference(self.props.model, self.props.model.get_path(iter))
                self.level_setup_event(r, device, cinfo)
                gobject.timeout_add(1000, update, r, cinfo, props["Address"])
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

        if adapter is not None and not re.match("hci[0-9]*", adapter):
            adapter = adapter_path_to_name(adapter)

        dprint(adapter)
        if self.Adapter is not None:
            self.adapter_signals.DisconnectAll()

        try:
            self.Adapter = self.Manager.GetAdapter(adapter)
            self.adapter_signals.Handle(self.Adapter, self.on_device_found, "DeviceFound")
            self.adapter_signals.Handle(self.Adapter, self.on_property_changed, "PropertyChanged")
            self.adapter_signals.Handle(self.Adapter, self.on_device_created, "DeviceCreated")
            self.adapter_signals.Handle(self.Adapter, self.on_device_removed, "DeviceRemoved")
            self.__adapter_path = self.Adapter.GetObjectPath()

            self.emit("adapter-changed", self.__adapter_path)
        except Bluez.errors.DBusNoSuchAdapterError as e:
            dprint(e)
            #try loading default adapter
            if len(self.Manager.ListAdapters()) > 0 and adapter != None:
                self.SetAdapter()
            else:
                self.Adapter = None
                self.emit("adapter-changed", None)

        except dbus.DBusServiceUnknownError:
            dprint("Dbus error while trying to get adapter.")
            self.Adapter = None
            self.emit("adapter-changed", None)


    def update_progress(self, time, totaltime):
        if not self.discovering:
            return False

        self.__discovery_time += time

        progress = self.__discovery_time / totaltime
        if progress >= 1.0:
            progress = 1.0
        #if self.__discovery_time >= totaltime:
        #self.StopDiscovery()
        #return False

        self.emit("discovery-progress", progress)
        return True


    def add_device(self, device, append=True):
        iter = self.find_device(device)
        #device belongs to another adapter
        if not device.Fake:
            if not device.get_object_path().startswith(self.Adapter.GetObjectPath()):
                return

        if iter == None:
            dprint("adding new device")
            if append:
                iter = self.liststore.append()
            else:
                iter = self.liststore.prepend()

            self.set(iter, device=device)
            self.row_setup_event(iter, device)

            props = device.GetProperties()
            try:
                self.set(iter, dbus_path=device.GetObjectPath())
            except:
                pass

            if not "Fake" in props:
                self.device_signals.Handle("bluez", device,
                                           self.on_device_property_changed,
                                           "PropertyChanged",
                                           sigid=device.GetObjectPath(),
                                           path_keyword="path")
                if props["Connected"]:
                    self.monitor_power_levels(device)


        else:
            row = self.get(iter, "device")
            existing_dev = row["device"]

            props = existing_dev.GetProperties()
            props_new = device.GetProperties()

            #turn a Fake device to a Real device
            n = not "Fake" in props and not "Fake" in props_new
            if n:
                dprint("Updating existing dev")
                self.device_signals.Disconnect(existing_dev.GetObjectPath())
            #existing_dev.Destroy()

            if ("Fake" in props and not "Fake" in props_new) or n:
                self.set(iter, device=device, dbus_path=device.GetObjectPath())
                self.row_setup_event(iter, device)

                if not n:
                    self.emit("device-property-changed", device, iter, ("Fake", False))
                    self.row_update_event(iter, "Fake", False)

                self.device_signals.Handle("bluez", device,
                                           self.on_device_property_changed,
                                           "PropertyChanged",
                                           sigid=device.GetObjectPath(),
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
        devices = self.Adapter.ListDevices()
        for device in devices:
            self.device_add_event(Device(device))

        if autoselect:
            self.selection.select_path(0)

    def DiscoverDevices(self, time=10.24):
        if not self.discovering:
            self.__discovery_time = 0
            self.Adapter.StartDiscovery()
            self.discovering = True
            T = 1.0 / 15 * 1000
            gobject.timeout_add(int(T), self.update_progress, T / 1000, time)

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
            self.Adapter.StopDiscovery()

    def PrependDevice(self, device):
        self.add_device(device, False)

    def AppendDevice(self, device):
        self.add_device(device, True)

    def RemoveDevice(self, device, iter=None, force=False):
        dprint(device)
        if iter == None:
            iter = self.find_device(device)

        if not device.Temp and self.compare(self.selected(), iter):
            self.emit("device-selected", None, None)

        try:
            props = device.GetProperties()
        except:
            self.device_signals.Disconnect(device.get_object_path())
        else:
            if not "Fake" in props:
                self.device_signals.Disconnect(device.GetObjectPath())

        if device.Temp and not force:
            dprint("converting to fake")

            props = copy.deepcopy(props)
            props["Fake"] = True
            dev = FakeDevice(props)

            device = Device(dev)
            self.device_add_event(device)

        else:
            #device.Destroy()
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
                self.RemoveDevice(device, iter, True)
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
                iter = self.props.model.get_iter(path)
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
                iter = self.props.model.get_iter(path)
                return iter
            else:
                del self.path_to_row[path]
                return None
        except KeyError:
            return None

    def do_cache(self, iter, kwargs):
        if "device" in kwargs:
            if kwargs["device"]:
                self.address_to_row[kwargs["device"].Address] = gtk.TreeRowReference(self.props.model,
                                                                                     self.props.model.get_path(iter))
                dprint("Caching new device %s" % kwargs["device"].Address)

        if "dbus_path" in kwargs:
            if kwargs["dbus_path"] != None:
                self.path_to_row[kwargs["dbus_path"]] = gtk.TreeRowReference(self.props.model,
                                                                             self.props.model.get_path(iter))
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


#	#searches for existing devices in the list
#	def find_device(self, device):
#   		for i in range(len(self.liststore)):
#   			row = self.get(i, "device")
#   			if device.Address == row["device"].Address:
#   				return self.get_iter(i)
#   		return None
# 
#   	def find_device_by_path(self, path):
#   		rows = self.get_conditional(dbus_path=path)
#   		if rows == []:
#   			return None
#   		else:
#   			return self.get_iter(rows[0])

