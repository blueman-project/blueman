# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gio, GLib
from blueman.gui.Notification import Notification
from blueman.Sdp import DIALUP_NET_SVCLASS_ID
from blueman.Functions import get_icon, composite_icon
import weakref
import logging


class ConnectionHandler:
    def __init__(self, parent, service, reply, err):
        self.parent = parent
        self.service = service
        self.reply = reply
        self.err = err
        self.rfcomm_dev = None
        self.timeout = None

        self.signal_sub = self.parent._bus.signal_subscribe("org.freedesktop.ModemManager1",
                                                            "org.freedesktop.DBus.ObjectManager",
                                                            "InterfacesAdded",
                                                            "/org/freedesktop/ModemManager1",
                                                            None,
                                                            Gio.DBusSignalFlags.NONE,
                                                            self.on_interfaces_added)

        # for some reason these handlers take a reference and don't give it back
        # so i have to workaround :(
        w = weakref.ref(self)
        service.connect(reply_handler=lambda *args: w() and w().on_connect_reply(*args),
                        error_handler=lambda *args: w() and w().on_connect_error(*args))

    def on_connect_reply(self, rfcomm):
        self.rfcomm_dev = rfcomm
        self.timeout = GLib.timeout_add(10000, self.on_timeout)

    def on_connect_error(self, *args):
        self.err(*args)
        self.cleanup()

    def cleanup(self):
        if self.timeout:
            GLib.source_remove(self.timeout)

        self.parent._bus.signal_unsubscribe(self.signal_sub)
        self.signal_sub = None
        self.service = None

    def on_mm_device_added(self, path, name="org.freedesktop.ModemManager"):
        logging.info(path)
        interface = "%s.Modem" % name
        res = self.parent._bus.call_sync(name, path, 'org.freedesktop.DBus.Properties', "GetAll",
                                         GLib.Variant("(s)", (interface,)),
                                         None, Gio.DBusCallFlags.NONE, GLib.MAXINT, None)
        props = res.unpack()[0]

        if self.rfcomm_dev and "bluetooth" in props["Drivers"] and self.rfcomm_dev.split('/')[-1] in props["Device"]:
            logging.info("It's our bluetooth modem!")

            modem = get_icon("modem", 24)
            blueman = get_icon("blueman", 48)

            icon = composite_icon(blueman, [(modem, 24, 24, 255)])

            Notification(
                _("Bluetooth Dialup"),
                _("DUN connection on %s will now be available in Network Manager") % self.service.device['Alias'],
                image_data=icon).show()

            self.reply(self.rfcomm_dev)
            self.cleanup()

    def on_interfaces_added(self, connection, sender_name, object_path, interface_name, signal_name, param):
        path, interfaces = param.unpack()
        if 'org.freedesktop.ModemManager1.Modem' in interfaces:
            self.on_mm_device_added(path, "org.freedesktop.ModemManager1")

    def on_timeout(self):
        self.timeout = None
        self.err(GLib.Error(_("Modem Manager did not support the connection")))
        self.cleanup()


class NMDUNSupport(AppletPlugin):
    __depends__ = ["StatusIcon", "DBusService"]
    __conflicts__ = ["PPPSupport"]
    __icon__ = "modem"
    __author__ = "Walmis"
    __description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager")
    __priority__ = 1

    def on_load(self):
        def on_dbus_connection_finnish(cancellable, result):
            self._bus = Gio.bus_get_finish(result)

        Gio.bus_get(Gio.BusType.SYSTEM, None, on_dbus_connection_finnish)

    def on_unload(self):
        pass

    def rfcomm_connect_handler(self, service, reply, err):
        if DIALUP_NET_SVCLASS_ID == service.short_uuid:
            ConnectionHandler(self, service, reply, err)
            return True
        else:
            return False
