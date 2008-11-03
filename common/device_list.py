from blueman.Gui.generic_list import generic_list
from blueman.Main.Device import Device
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
		#gobject.__init__(self);
		try:
			self.manager = Bluez.Manager("gobject")
		except:
			self.manager = None
			
		self.__discovery_time = 0
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
		
		self.filter = self.liststore.filter_new()
		self.filter.set_visible_func(self.is_visible)
		
	def is_visible(self, model, iter):
		print model, iter
		
		#todo: padaryti filtravima
		
		return True
		
		
	def on_selection_changed(self, selection):
		iter = self.selected()
		row = self.get(iter, "device")
		dev = row["device"]
		self.emit("device-selected", dev, iter)
		
		
	def on_adapter_change(self):
		#todo
		pass
		
		
	def on_device_found(self, address, props):
		try:
			dev = self.adapter.FindDevice(address)
		except:
			props["Address"] = address
			props["Fake"] = True
			dev = Device(props)
		
		self.emit("device-found", dev)
		self.AppendDevice(dev)
		
	
	def on_property_changed(self, key, value):
		self.emit("adapter-property-changed", self.adapter, (key, value))
				
				
	def on_device_property_changed(self, key, value, path):
		dev = Bluez.Device(path)
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
			props = device.GetProperties()
			if not self.iter_is_valid(iter) or not props["Connected"]:
				print "stopping monitor"
				cinfo.deinit()
				return False
			else:
				self.level_setup_event(iter, device, cinfo)
				return True
		
		
		props = device.GetProperties()
		print "starting monitor", props
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
		except:
			self.adapter = None
			

		
	def DisplayKnownDevices(self):
		self.clear()
		devices = self.adapter.ListDevices()
		for device in devices:
			self.device_add_event(device)



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
		
	def DiscoverDevices(self, time=10):
		self.__discovery_time = 0
		self.adapter.StartDiscovery()
		self.discovering = True
		T = 1.0/24*1000 #24fps
		gobject.timeout_add(int(T), self.update_progress, T/1000, time)

		
	def StopDiscovery(self):
		self.discovering = False
		self.adapter.StopDiscovery()
		
	
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
		
	def SetFilter(self):
		#todo
		pass
	
	

