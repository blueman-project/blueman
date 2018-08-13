from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.main.Mechanism import Mechanism
from blueman.main.Config import Config

from gi.repository import GObject

from blueman.Sdp import uuid128_to_uuid16, DIALUP_NET_SVCLASS_ID
import os


class Connection:
    def __init__(self, applet, service, port, ok, err):
        self.reply_handler = ok
        self.error_handler = err
        self.service = service
        self.port = port
        self.Applet = applet

        res = os.popen("ps ax -o pid,args | grep [M]odemManager").read()
        if not res:
            self.connect()
        else:
            timeout = 10
            dprint("ModemManager is running, delaying connection %ssec for it to complete probing" % timeout)
            GLib.timeout_add_seconds(timeout, self.connect)

    def connect(self):
        c = Config("org.blueman.gsmsetting", "/org/blueman/gsmsettings/%s/" % self.service.device.Address)

        m = Mechanism()
        m.PPPConnect(self.port, c["number"], c["apn"], reply_handler=self.on_connected,
                     error_handler=self.on_error, timeout=200)

    def on_error(self, error):
        self.error_handler(error)
        GObject.timeout_add(1000, self.service.disconnect, int(self.port[-1]))

    def on_connected(self, iface):
        self.reply_handler(self.port)
        self.Applet.Plugins.Run("on_ppp_connected", self.service.device, self.port, iface)

        msg = _("Successfully connected to <b>DUN</b> service on <b>%(0)s.</b>\n"
                "Network is now available through <b>%(1)s</b>") % {"0": self.service.device.Alias, "1": iface}

        Notification(_("Connected"), msg, pixbuf=get_icon("network-wireless", 48),
                     status_icon=self.Applet.Plugins.StatusIcon)


class PPPSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __description__ = _("Provides basic support for connecting to the internet via DUN profile.")
    __author__ = "Walmis"
    __icon__ = "modem"
    __priority__ = 0

    def on_load(self, applet):
        AppletPlugin.add_method(self.on_ppp_connected)

    def on_unload(self):
        pass

    def on_ppp_connected(self, device, rfcomm, ppp_port):
        pass

    def on_rfcomm_connected(self, service, port):
        pass

    def rfcomm_connect_handler(self, service, reply, err):
        if DIALUP_NET_SVCLASS_ID == uuid128_to_uuid16(service.uuid):
            def local_reply(port):
                Connection(self.Applet, service, port, reply, err)

            service.connect(reply_handler=local_reply, error_handler=err)
            dprint("Connecting rfcomm device")

            return True
        else:
            return False
