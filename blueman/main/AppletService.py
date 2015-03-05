from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from dbus.mainloop.glib import DBusGMainLoop
from blueman.main.SignalTracker import SignalTracker

DBusGMainLoop(set_as_default=True)

class AppletService(dbus.proxies.Interface, SignalTracker):
    __inst__ = None

    def __new__(c):
        if not AppletService.__inst__:
            AppletService.__inst__ = object.__new__(c)

        return AppletService.__inst__

    def __init__(self):
        SignalTracker.__init__(self)
        self.bus = dbus.SessionBus()

        service = self.bus.get_object("org.blueman.Applet", "/", follow_name_owner_changes=True)
        dbus.proxies.Interface.__init__(self, service, "org.blueman.Applet")

    def Handle(self, signame, handler):
        SignalTracker.Handle(self, "dbus", self.bus, handler, signame, self.dbus_interface, path=self.object_path)
