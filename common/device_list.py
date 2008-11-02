from blueman.Gui.generic_list import generic_list
from blueman.Main.Device import Device
import blueman.Bluez as Bluez
import gtk
import gobject



class device_list(generic_list):
	__gsignals__ = {
		#@param: device
		'device-found' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		#@param: device TreeIter
		'device-selected' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT,)),
		#@param: tuple (key, value)
		'device-property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
		#@param: tuple (key, value)
		'adapter-property-changed' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,)),
	}


	def __init__(self, adapter=None):
		#gobject.__init__(self);
		try:
			self.manager = Bluez.Manager("gobject")
		except:
			self.manager = None
		

		self.SetAdapter(adapter)

		data = [
			#device picture
			["device_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":0}, None],
			
			#device caption
			["caption", str, gtk.CellRendererText(), {"markup":1}, None, {"expand": True}],

			["device", object],

			
			["rssi_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":3}, None, {"spacing": 0}],
			["lq_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":4}, None, {"spacing": 0}],
			["tpl_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":5}, None, {"spacing": 0}],
			
			["bonded_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":6}, None, {"spacing": 0}],
			["trusted_pb", 'GdkPixbuf', gtk.CellRendererPixbuf(), {"pixbuf":7}, None, {"spacing": 0}],
			
			["connected", bool],
			["bonded", bool],
			["trusted", bool],	
			
			["rssi", float],
			["lq", float],
			["tpl", float],
			["dbus_path", str]
			#["test", 'PyObject', CellRendererPixbufTable(), {"pixbuffs":16}, None]
		
		]
		generic_list.__init__(self, data)
		
		self.connect("cursor-changed", self.on_cursor_changed)
		
		
	def on_cursor_changed(self, treeview):
		row = self.get(self.selected(), "device")
		dev = row["device"]
		self.emit("device-selected", dev)
		
	def on_connection_change(self):
		pass
		
	def on_adapter_change(self):
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
		self.emit("adapter-property-changed", (key, value))
				
				
	def on_device_property_changed(self, key, value, path):
		dev = Bluez.Device(path)
		iter = self.find_device(dev)
		self.row_update_event(iter, key, value)
		
		self.emit("device-property-changed", (key, value))
	
	##### virtual funcs #####
	
	#called when power levels need updating
	def level_setup_event(self, iter, device, conn_info):
		pass
	
	#called when row needs to be initialized
	def row_setup_event(self, iter, device):
		pass
		
	#called when a property for a device changes
	def row_update_event(self, iter, key, value):
		pass
		
	#called when device is created
	def on_device_created(self, path):
		dev = Bluez.Device(path)
		self.AppendDevice(dev)
	
	#called when device is removed
	def on_device_removed(self, path):
		iter = self.find_device_by_path(path)
		row = self.get(iter, "device")
		dev = row["device"]
		self.RemoveDevice(dev, iter)
		
		
	#########################
	
	def SetAdapter(self, adapter=None):
		try:
			self.adapter = self.manager.GetAdapter(adapter)
		except:
			self.adapter = None
			
		self.adapter.HandleSignal(self.on_device_found, "DeviceFound")
		self.adapter.HandleSignal(self.on_property_changed, "PropertyChanged")
		self.adapter.HandleSignal(self.on_device_created, "DeviceCreated")
		self.adapter.HandleSignal(self.on_device_removed, "DeviceRemoved")
		
	def DisplayKnownDevices():
		pass
		

		
	def DiscoverDevices(self):
		self.adapter.StartDiscovery()
		
		pass
		
	def StopDiscovery(self):
		pass
		
	
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

		
	def AppendDevice(self, device):
		iter = self.find_device(device)
		if iter == None:

			iter = self.append(device_pb=None, 
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
					)

			self.row_setup_event(iter, device)
			
			props = device.GetProperties()
			try:
				self.set(iter, dbus_path=device.GetObjectPath())
			except:
				pass
			
			if not "Fake" in props:
				device.HandleSignal(self.on_device_property_changed, "PropertyChanged", path_keyword="path")
		
		
		else:
			row = self.get(iter, "device")
			existing_dev = row["device"]
			
			props = existing_dev.GetProperties()
			props_new = device.GetProperties()
			if "Fake" in props and not "Fake" in props_new:
				self.set(iter, device=device, dbus_path=device.GetObjectPath())
				self.row_setup_event(iter, device)
	
	def PrependDevice(self):
		pass
		
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
		pass
	
	

