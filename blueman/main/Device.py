from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
import inspect
from blueman.Functions import dprint
from blueman.Sdp import uuid128_to_uuid16
from blueman.main.SignalTracker import SignalTracker
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device as BluezDevice
from blueman.Service import Service
import blueman.services
import blueman.services.meta
import os
import weakref


class Device(GObject.GObject):
    __gsignals__ = {
        str('invalidated'): (GObject.SignalFlags.NO_HOOKS, None, ()),
        str('property-changed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, instance):
        GObject.GObject.__init__(self)

        self.Properties = {}
        self.Fake = True
        self.Temp = False

        if hasattr(instance, "format") and hasattr(instance, "upper"):
            self.Device = BluezDevice(instance)
        else:
            self.Device = instance

        #set fallback icon, fixes lp:#327718
        self.Device.Icon = "blueman"
        self.Device.Class = "unknown"
        self.Device.Appearance = 0

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

    def get_service(self, uuid):
        for name, cls in inspect.getmembers(blueman.services, inspect.isclass):
            if uuid128_to_uuid16(uuid) == cls.__svclass_id__:
                return cls(self, uuid)

    def get_services(self):
        if self.Fake:
            return []
        services = (self.get_service(uuid) for uuid in self.UUIDs)
        return [service for service in services if service]

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

    def Copy(self):
        if not self.Valid:
            raise Exception("Attempted to copy an invalidated device")
        return Device(self.Device)

    def property_changed(self, key, value):
        self.emit("property-changed", key, value)
        self.Properties[key] = value

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
