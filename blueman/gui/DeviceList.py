# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

from blueman.gui.GenericList import GenericList
from blueman.main.FakeDevice import FakeDevice
from blueman.main.Device import Device
from blueman.DeviceClass import get_major_class

from blueman.Lib import conn_info
import blueman.bluez as Bluez
import gtk
import gobject
import re

from blueman.Functions import adapter_path_to_name

class DeviceList(GenericList):
	__gsignals__ = {
		#@param: device
		'device-found' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		#@param: device TreeIter
		#note: None None is given when there ar no more rows, or when selected device is removed
		'device-selected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: device, TreeIter, (key, value)
		#note: there is a special property "Fake", it's not a real property, 
		#but it is used to notify when device changes state from "Fake" to a real BlueZ object
		#the callback would be called with Fake=False
		'device-property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: adapter, (key, value)
		'adapter-property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: progress (0 to 1)
		'discovery-progress' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
		
		#@param: new adapter path, None if there are no more adapters
		'adapter-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		
		#@param: adapter path
		'adapter-added' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		'adapter-removed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
	}


	def __init__(self, adapter=None, tabledata=[]):
		def on_adapter_removed(path):
			self.emit("adapter-removed", path)
			if path == self.__adapter_path:
				self.clear()
				self.Adapter = None
				self.SetAdapter()	
				
		def on_adapter_added(path):
			def property_changed(key, val):
				if key == "Powered":
					self.emit("adapter-added", path)
					a.UnHandleSignal(property_changed, "PropertyChanged")
						
					if self.Adapter == None:
						self.SetAdapter(path)	

								
			
			a = Bluez.Adapter(path)
			a.HandleSignal(property_changed, "PropertyChanged")
			#gobject.timeout_add(50, self.emit, "adapter-added", path)
			#self.emit("adapter-added", path)

		
		
		try:
			self.Manager = Bluez.Manager("gobject")
			self.Manager.HandleSignal(on_adapter_removed, "AdapterRemoved")
			self.Manager.HandleSignal(on_adapter_added, "AdapterAdded")
		except:
			self.Manager = None
			
		self.__discovery_time = 0
		self.__adapter_path = None
		self.Adapter = None
		self.discovering = False
		

		
		data = []
		data = data + tabledata

		data = data +	[
			["device", object],
			["dbus_path", str]
		]
		
		GenericList.__init__(self, data)
		
		self.SetAdapter(adapter)
		
		self.selection.connect("changed", self.on_selection_changed)
		
		
	def on_selection_changed(self, selection):
		iter = self.selected()
		if iter:
			row = self.get(iter, "device")
			dev = row["device"]
			self.emit("device-selected", dev, iter)
		
		

		
	def on_device_found(self, address, props):
		if self.discovering:

			try:
				dev = self.Adapter.FindDevice(address)
			except:
				props["Address"] = address
				props["Fake"] = True
				dev = FakeDevice(props)
			
			device = Device(dev)
		
			self.emit("device-found", device)
			self.device_add_event(device)
		
	
	def on_property_changed(self, key, value):
		print "adapter propery changed", key, value
		self.emit("adapter-property-changed", self.Adapter, (key, value))
				
				
	def on_device_property_changed(self, key, value, path, *args):
		print "list: device_prop_ch", key, value, path, args

		iter = self.find_device_by_path(path)
		
		if iter != None:
			dev = self.get(iter, "device")["device"]
			self.row_update_event(iter, key, value)
		
			self.emit("device-property-changed", dev, iter, (key, value))
		
			if key == "Connected":
				if value:
					self.monitor_power_levels(dev)
				else:
				
					self.level_setup_event(iter, dev, None)
		
		
	def monitor_power_levels(self, device):
		def update(iter, device, cinfo):
			if not device.Connected or not self.find_device(device):
				print "stopping monitor"
				cinfo.deinit()
				return False
			else:
				self.level_setup_event(iter, device, cinfo)
				return True
		
		
		props = device.GetProperties()
		print "starting monitor"
		if "Connected" in props and props["Connected"]:
			iter = self.find_device(device)
			
			
			hci = re.search(".*(hci[0-9]*)", self.Adapter.GetObjectPath()).groups(0)[0]
			cinfo = conn_info(props["Address"], hci)
			self.level_setup_event(iter, device, cinfo)
			gobject.timeout_add(1000, update, iter, device, cinfo)
		
	
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
		
	def device_remove_event(self, device):
		pass
		
	
	#########################
	
	def on_device_created(self, path):
		print "created", path
		dev = Bluez.Device(path)
		dev = Device(dev)
		self.device_add_event(dev)
		
	
	def on_device_removed(self, path):
		iter = self.find_device_by_path(path)
		row = self.get(iter, "device")
		dev = row["device"]
		self.RemoveDevice(dev, iter)
		self.device_remove_event(dev)
	
	
	def SetAdapter(self, adapter=None):
		self.clear()
		if self.discovering:
			self.emit("adapter-property-changed", self.Adapter, ("Discovering", False))
			self.StopDiscovery()
		
		if adapter != None and not re.match("hci[0-9]*", adapter):
			print "path to"
			adapter = adapter_path_to_name(adapter)
		
		print adapter
		if self.Adapter != None:
			self.Adapter.UnHandleSignal(self.on_device_found, "DeviceFound")
			self.Adapter.UnHandleSignal(self.on_property_changed, "PropertyChanged")
			self.Adapter.UnHandleSignal(self.on_device_created, "DeviceCreated")
			self.Adapter.UnHandleSignal(self.on_device_removed, "DeviceRemoved")
		
		try:
			self.Adapter = self.Manager.GetAdapter(adapter)
			self.Adapter.HandleSignal(self.on_device_found, "DeviceFound")
			self.Adapter.HandleSignal(self.on_property_changed, "PropertyChanged")
			self.Adapter.HandleSignal(self.on_device_created, "DeviceCreated")
			self.Adapter.HandleSignal(self.on_device_removed, "DeviceRemoved")
			self.__adapter_path = self.Adapter.GetObjectPath()
			
			self.emit("adapter-changed", self.__adapter_path)
		except Bluez.errors.DBusNoSuchAdapterError:
			#try loading default adapter
			if len(self.Manager.ListAdapters()) > 0:
				self.SetAdapter()
			else:
				self.Adapter = None
				self.emit("adapter-changed", None)
			
		
			

		
	def update_progress(self, time, totaltime):
		if not self.discovering:
			return False
		
		self.__discovery_time += time
			
		progress = self.__discovery_time / totaltime
		
		if self.__discovery_time >= totaltime:
			self.StopDiscovery()
			return False

		self.emit("discovery-progress", progress)
		return True
		
	
	#searches for existing devices in the list
	def find_device(self, device):
   		for i in range(len(self.liststore)):
   			row = self.get(i, "device")
   			if device.Address == row["device"].Address:
   				return self.get_iter(i)
   		return None
   		
   	def find_device_by_path(self, path):
   		rows = self.get_conditional(dbus_path=path)
   		if rows == []:
   			return None
   		else:
   			return self.get_iter(rows[0])

		
	def add_device(self, device, append=True):
		iter = self.find_device(device)
		if iter == None:
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
				device.HandleSignal(self.on_device_property_changed, "PropertyChanged", path_keyword="path")
				if props["Connected"]:
					self.monitor_power_levels(device)
		
		
		else:
			row = self.get(iter, "device")
			existing_dev = row["device"]
			
			props = existing_dev.GetProperties()
			props_new = device.GetProperties()
			if "Fake" in props and not "Fake" in props_new:
				self.set(iter, device=device, dbus_path=device.GetObjectPath())
				self.row_setup_event(iter, device)
				self.emit("device-property-changed", device, iter, ("Fake", False))
				self.row_update_event(iter, "Fake", False)
				
				device.HandleSignal(self.on_device_property_changed, "PropertyChanged", path_keyword="path")
				if props_new["Connected"]:
					self.monitor_power_levels(device)
	
	
	def DisplayKnownDevices(self, autoselect=False):
		self.clear()
		devices = self.Adapter.ListDevices()
		for device in devices:
			self.device_add_event(Device(device))
			
		if autoselect:
			self.selection.select_path(0)
	
	def DiscoverDevices(self, time=10):
		self.__discovery_time = 0
		self.Adapter.StartDiscovery()
		self.discovering = True
		T = 1.0/24*1000 #24fps
		gobject.timeout_add(int(T), self.update_progress, T/1000, time)

	def IsValidAdapter(self):
		if self.Adapter == None:
			return False
		else:
			return True
		
		
	def StopDiscovery(self):
		self.discovering = False
		if self.Adapter != None:
			self.Adapter.StopDiscovery()
	
	def PrependDevice(self, device):
		self.add_device(device, False)
		
	def AppendDevice(self, device):
		self.add_device(device, True)
		
	def RemoveDevice(self, device, iter=None):
		if iter == None:
			iter = self.find_device(device)
		
		if self.compare(self.selected(), iter):
			self.emit("device-selected", None, None)
		
		try:
			props = device.GetProperties()
		except:
			device.UnHandleSignal(self.on_device_property_changed, "PropertyChanged")
		else:
			if not "Fake" in props:
				device.UnHandleSignal(self.on_device_property_changed, "PropertyChanged")
				
		device.Destroy()
				
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
	

