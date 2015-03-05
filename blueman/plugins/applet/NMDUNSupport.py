from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.AppletPlugin import AppletPlugin
import dbus
from gi.repository import GObject
from blueman.main.SignalTracker import SignalTracker
from blueman.gui.Notification import Notification
from blueman.Sdp import uuid128_to_uuid16, DIALUP_NET_SVCLASS_ID
from blueman.Functions import get_icon, composite_icon, dprint
import weakref


class ConnectionHandler:
    def __init__(self, parent, service, reply, err):
        self.parent = parent
        self.service = service
        self.reply = reply
        self.err = err
        self.rfcomm_dev = None
        self.timeout = None

        self.signals = SignalTracker()

        # ModemManager 0.x
        self.signals.Handle("dbus", self.parent.bus, self.on_mm_device_added, "DeviceAdded",
                            "org.freedesktop.ModemManager")
        # ModemManager 1.x
        self.signals.Handle("dbus", self.parent.bus, self.on_interfaces_added, "InterfacesAdded",
                            "org.freedesktop.DBus.ObjectManager")

        # for some reason these handlers take a reference and don't give it back
        #so i have to workaround :(
        w = weakref.ref(self)
        service.connect(reply_handler=lambda *args: w() and w().on_connect_reply(*args),
                        error_handler=lambda *args: w() and w().on_connect_error(*args))

    def __del__(self):
        dprint("deleting")

    def on_connect_reply(self, rfcomm):
        self.rfcomm_dev = rfcomm
        self.timeout = GObject.timeout_add(10000, self.on_timeout)

    def on_connect_error(self, *args):
        self.err(*args)
        self.cleanup()

    def cleanup(self):
        if self.timeout:
            GObject.source_remove(self.timeout)
        self.signals.DisconnectAll()

        del self.service

    def on_mm_device_added(self, path, name="org.freedesktop.ModemManager"):
        dprint(path)
        interface = "%s.Modem" % name
        props = self.parent.bus.call_blocking(name, path, "org.freedesktop.DBus.Properties", "GetAll", "s", [interface])

        try:
            drivers = props["Drivers"]
        except KeyError:
            drivers = [props["Driver"]]

        if self.rfcomm_dev and "bluetooth" in drivers and props["Device"] in self.rfcomm_dev:
            dprint("It's our bluetooth modem!")

            modem = get_icon("modem", 24)
            blueman = get_icon("blueman", 48)

            icon = composite_icon(blueman, [(modem, 24, 24, 255)])

            Notification(_("Bluetooth Dialup"),
                         _("DUN connection on %s will now be available in Network Manager") % self.service.device.Alias,
                         pixbuf=icon,
                         status_icon=self.parent.Applet.Plugins.StatusIcon)

            self.reply(self.rfcomm_dev)
            self.cleanup()

    def on_interfaces_added(self, object_path, interfaces):
        if 'org.freedesktop.ModemManager1.Modem' in interfaces:
            self.on_mm_device_added(object_path, "org.freedesktop.ModemManager1")

    def on_timeout(self):
        self.timeout = None
        self.err(dbus.DBusException(_("Modem Manager did not support the connection")))
        self.cleanup()


class NMDUNSupport(AppletPlugin):
    __depends__ = ["StatusIcon", "DBusService"]
    __conflicts__ = ["PPPSupport"]
    __icon__ = "modem"
    __author__ = "Walmis"
    __description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager")
    __priority__ = 1

    def on_load(self, applet):
        self.bus = dbus.SystemBus()

    def on_unload(self):
        pass

    def rfcomm_connect_handler(self, service, reply, err):
        if DIALUP_NET_SVCLASS_ID == uuid128_to_uuid16(service.uuid):
            ConnectionHandler(self, service, reply, err)
            return True
        else:
            return False
