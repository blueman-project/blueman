from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
import inspect
from blueman.Functions import dprint
from blueman.Sdp import uuid128_to_uuid16
from blueman.bluez import Manager
import blueman.services
import blueman.services.meta
import weakref


class Device(GObject.GObject):
    __gsignals__ = {
        str('invalidated'): (GObject.SignalFlags.NO_HOOKS, None, ()),
        str('property-changed'): (GObject.SignalFlags.NO_HOOKS, None, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT,)),
    }

    def __init__(self, instance):
        GObject.GObject.__init__(self)

        self.Properties = {}
        self.Temp = False

        self.Device = instance

        #set fallback icon, fixes lp:#327718
        self.Device.Icon = "blueman"
        self.Device.Class = "unknown"

        self.Valid = True

        dprint("caching initial properties")
        self.Properties = self.Device.get_properties()

        w = weakref.ref(self)
        self._obj_path = self.Device.get_object_path()
        self.Device.connect_signal('property-changed',
                                   lambda _device, key, value, _path: w() and w().property_changed(key, value))
        self._manager = Manager()
        self._manager.connect_signal('device-removed', lambda _adapter, path: w() and w().on_device_removed(path))

    def get_service(self, uuid):
        for name, cls in inspect.getmembers(blueman.services, inspect.isclass):
            if uuid128_to_uuid16(uuid) == cls.__svclass_id__:
                return cls(self, uuid)

    def get_services(self):
        services = (self.get_service(uuid) for uuid in self.UUIDs)
        return [service for service in services if service]

    def __del__(self):
        dprint("deleting device", self.get_object_path())
        self.Destroy()

    def get_object_path(self):
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
