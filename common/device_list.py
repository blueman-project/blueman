#
#
# blueman
# (c) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

from blueman.Gui.generic_list import generic_list
from blueman.Main.FakeDevice import FakeDevice
from blueman.Main.Device import Device
from blueman.device_class import get_major_class

from blueman.Lib import conn_info
import blueman.Bluez as Bluez
import gtk
import gobject
import re



class device_list(generic_list):
	__gsignals__ = {
		#@param: device
		'device-found' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		#@param: device TreeIter
		'device-selected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: device, (key, value)
		'device-property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: adapter, (key, value)
		'adapter-property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: progress (0 to 1)
		'discovery-progress' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_FLOAT,)),
	}


	def __init__(self, adapter=None, tabledata=[]):
		def on_adapter_removed(path):
			if path == self.__adapter_path:
				self.clear()
				self.SetAdapter()		
		
		
		try:
			self.manager = Bluez.Manager("gobject")
			self.manager.HandleSignal(on_adapter_removed, "AdapterRemoved")
		except:
			self.manager = None
			
		self.__discovery_time = 0
		self.__adapter_path = None
		self.adapter = None
		self.discovering = False
		

		self.SetAdapter(adapter)
		data = []
		data = data + tabledata

		data = data +	[
			["device", object],
			["dbus_path", str]
		]
		
		generic_list.__init__(self, data)
		
		
		self.selection.connect("changed", self.on_selection_changed)
		
		self.filter = "handheld"
		
		
	def on_selection_changed(self, selection):
		iter = self.selected()
		row = self.get(iter, "device")
		dev = row["device"]
		self.emit("device-selected", dev, iter)
		
		

		
	def on_device_found(self, address, props):
		if self.discovering:
			try:
				dev = self.adapter.FindDevice(address)
			except:
				props["Address"] = address
				props["Fake"] = True
				dev = FakeDevice(props)
			
			device = Device(dev)
		
			self.emit("device-found", device)
			self.device_add_event(device)
		
	
	def on_property_changed(self, key, value):
		self.emit("adapter-property-changed", self.adapter, (key, value))
				
				
	def on_device_property_changed(self, key, value, path):
		dev = Bluez.Device(path)
		dev = Device(dev)
		iter = self.find_device(dev)
		self.row_update_event(iter, key, value)
		
		self.emit("device-property-changed", dev, (key, value))
		
		if key == "Connected":
			if value:
				self.monitor_power_levels(dev)
			else:
				
				self.level_setup_event(iter, dev, None)
		
		
	def monitor_power_levels(self, device):
		def update(iter, device, cinfo):
			
			if not self.iter_is_valid(iter) or not device.GetProperties()["Connected"]:
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
			
			
			hci = re.search(".*(hci[0-9]*)", self.adapter.GetObjectPath()).groups(0)[0]
			cinfo = conn_info(props["Address"], hci)
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
		
	
	#########################
	
	def on_device_created(self, path):
		dev = Bluez.Device(path)
		dev = Device(dev)
		self.device_add_event(dev)
		
	
	def on_device_removed(self, path):
		iter = self.find_device_by_path(path)
		row = self.get(iter, "device")
		dev = row["device"]
		self.RemoveDevice(dev, iter)
	
	def SetAdapter(self, adapter=None):
		if self.adapter != None:
			self.adapter.UnHandleSignal(self.on_device_found, "DeviceFound")
			self.adapter.UnHandleSignal(self.on_property_changed, "PropertyChanged")
			self.adapter.UnHandleSignal(self.on_device_created, "DeviceCreated")
			self.adapter.UnHandleSignal(self.on_device_removed, "DeviceRemoved")
		
		try:
			self.adapter = self.manager.GetAdapter(adapter)
			self.adapter.HandleSignal(self.on_device_found, "DeviceFound")
			self.adapter.HandleSignal(self.on_property_changed, "PropertyChanged")
			self.adapter.HandleSignal(self.on_device_created, "DeviceCreated")
			self.adapter.HandleSignal(self.on_device_removed, "DeviceRemoved")
			self.__adapter_path = self.adapter.GetObjectPath()
		except:
			self.adapter = None
			

		
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
		props1 = device.GetProperties()
   		for i in range(len(self.liststore)):
   			row = self.get(i, "device")
   			props2 = row["device"].GetProperties()
   			if props1["Address"] == props2["Address"]:
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
				'''iter = self.append(device_pb=None, 
						caption="", 
						device=device,
						rssi_pb=None,
						lq_pb=None,
						tpl_pb=None,
						bonded_pb=None,
						trusted_pb=None,
						connected=False,
						bonded=False,
						trusted=False,
						rssi=-1,
						lq=-1,
						tpl=-1,
						dbus_path=""
						)'''
			else:
				iter = self.liststore.prepend()
				'''iter = self.prepend(device_pb=None, 
					caption="", 
					device=device,
					rssi_pb=None,
					lq_pb=None,
					tpl_pb=None,
					bonded_pb=None,
					trusted_pb=None,
					connected=False,
					bonded=False,
					trusted=False,
					rssi=-1,
					lq=-1,
					tpl=-1,
					dbus_path=""
					)'''
			
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
	
	
	def DisplayKnownDevices(self):
		self.clear()
		devices = self.adapter.ListDevices()
		for device in devices:
			self.device_add_event(Device(device))
	
	def DiscoverDevices(self, time=10):
		self.__discovery_time = 0
		self.adapter.StartDiscovery()
		self.discovering = True
		T = 1.0/24*1000 #24fps
		gobject.timeout_add(int(T), self.update_progress, T/1000, time)

		
	def StopDiscovery(self):
		self.discovering = False
		self.adapter.StopDiscovery()
	
	def PrependDevice(self, device):
		self.add_device(device, False)
		
	def AppendDevice(self, device):
		self.add_device(device, True)
		
	def RemoveDevice(self, device, iter=None):
		if iter == None:
			iter = self.find_device(device)
		
		self.delete(iter)
		
		try:
			props = device.GetProperties()
		except:
			device.UnHandleSignal(self.on_device_property_changed, "PropertyChanged")
		else:
			if not "Fake" in props:
				device.UnHandleSignal(self.on_device_property_changed, "PropertyChanged")
				
	def clear(self):
		for i in self.liststore:
			iter = i.iter
			device = self.get(iter, "device")["device"]
			self.RemoveDevice(device, iter)
	
		
	def SetFilter(self):
		self.clear()
		
		def is_visible(self, model, iter):
		#print model, iter
		
		print "Filter", iter
		if self.filter_type != None:
			device = self.get(iter, "device")["device"]
			
			maj_class = get_major_class(device.Class)
			if maj_class != self.filter_type:

				return True
			
		
		
		return True
	
	

