from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject
import dbus
from blueman.main.SignalTracker import SignalTracker


class OdsBase(dbus.proxies.Interface, GObject.GObject):
    # def OdsMethod(fn):
    #		def new(self, *args, **kwargs):

    #			fn(self, *args, **kwargs)
    #			getattr(super(OdsBase,self), fn.__name__)(*args, **kwargs)
    #		return new

    def __init__(self, service_name, obj_path):
        self.bus = dbus.SessionBus()
        self._signals = SignalTracker()

        service = self.bus.get_object("org.openobex", obj_path)
        GObject.GObject.__init__(self)
        dbus.proxies.Interface.__init__(self, service, service_name)

    def DisconnectAll(self):
        self._signals.DisconnectAll()

    def Handle(self, signame, handler):
        self._signals.Handle("dbus", self.bus, handler, signame, self.dbus_interface, None, self.object_path)

    def GHandle(self, *args):
        self._signals.Handle("gobject", self, *args)

