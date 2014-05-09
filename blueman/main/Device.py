from gi.repository import GObject
from blueman.Functions import dprint
from blueman.main.SignalTracker import SignalTracker
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device as BluezDevice
import os
import weakref


class Device(GObject.GObject):
    __gsignals__ = {
        'invalidated': (GObject.SignalFlags.NO_HOOKS, None, ()),
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, instance):
        GObject.GObject.__init__(self)

        self.Properties = {}
        self.Fake = True
        self.Temp = False

        if isinstance(instance, str) or isinstance(instance, unicode):
            self.Device = BluezDevice(instance)
        else:
            self.Device = instance

        #set fallback icon, fixes lp:#327718
        self.Device.Icon = "blueman"
        self.Device.Class = "unknown"

        self.__services = {}

        self.Valid = True

        self.Signals = SignalTracker()

        dprint("caching initial properties")
        self.Properties = self.Device.get_properties()

        if not "Fake" in self.Properties:
            self.Fake = False

        w = weakref.ref(self)
        if not self.Fake:
            self._obj_path = self.Device.get_object_path()
            self.Signals.Handle("bluez", self.Device, lambda key, value: w() and w().property_changed(key, value),
                                "PropertyChanged")
            object_path = self.Device.get_object_path()
            adapter = Adapter(object_path.replace("/" + os.path.basename(object_path), ""))
            self.Signals.Handle("bluez", adapter, lambda path: w() and w().on_device_removed(path), "DeviceRemoved")

    @property
    def Services(self):
        if len(self.__services) == 0:
            self.init_services()

        return self.__services

    def __del__(self):
        dprint("deleting device", self.get_object_path())
        self.Destroy()

    def get_object_path(self):
        if not self.Fake:
            return self._obj_path

    def on_device_removed(self, path):
        if path == self._obj_path:
            self.emit("invalidated")
            self.Destroy()

    def init_services(self):
        dprint("Loading services")

        if not self.Fake:
            services = self.Device.list_services()
            self.__services = {}
            for service in services:
                name = service.get_interface_name().split(".")
                if name[0] == 'org' and name[1] == 'bluez':
                    name = name[2].lower()
                    if name.endswith('1'):
                        name = name[:-1]
                    self.__services[name] = service

    def Copy(self):
        if not self.Valid:
            raise Exception("Attempted to copy an invalidated device")
        return Device(self.Device)

    def property_changed(self, key, value):
        self.emit("property-changed", key, value)
        self.Properties[key] = value
        if key == "UUIDs":
            self.init_services()

    def Destroy(self):
        dprint("invalidating device", self.get_object_path())
        self.Valid = False
        #self.Device = None
        self.Signals.DisconnectAll()

    #def __del__(self):
    #	dprint("DEBUG: deleting Device instance")

    def get_properties(self):
        #print "Properties requested"
        if not self.Valid:
            raise Exception("Attempted to get properties for an invalidated device")
        return self.Properties

    def __getattr__(self, name):
        if name in self.__dict__["Properties"]:
            if not self.Valid:
                #traceback.print_stack()
                dprint("Warning: Attempted to get %s property for an invalidated device" % name)
            return self.__dict__["Properties"][name]
        else:
            return getattr(self.Device, name)

    def __setattr__(self, key, value):
        if not key in self.__dict__ and "Properties" in self.__dict__ and key in self.__dict__["Properties"]:
            if not self.Valid:
                raise Exception("Attempted to set properties for an invalidated device")
            dprint("Setting property", key, value)
            self.__dict__["Device"].set(key, value)
        else:
            self.__dict__[key] = value
