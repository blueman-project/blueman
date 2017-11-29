# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.main.Mechanism import Mechanism
from blueman.main.Config import Config

from gi.repository import GLib

from blueman.Sdp import DIALUP_NET_SVCLASS_ID
import os
import logging


class Connection:
    def __init__(self, applet, service, port, ok, err):
        self.reply_handler = ok
        self.error_handler = err
        self.service = service
        self.port = port
        self.Applet = applet

        res = os.popen("ps x -o pid,args | grep [M]odemManager").read()
        if not res:
            self.connect()
        else:
            logging.info("ModemManager is running, delaying connection 5sec for it to complete probing")
            GLib.timeout_add(5000, self.connect)

    def connect(self):
        c = Config("org.blueman.gsmsettings", "/org/blueman/gsmsettings/%s/" % self.service.device['Address'])

        m = Mechanism()
        m.PPPConnect('(sss)', self.port, c["number"], c["apn"], result_handler=self.on_connected,
                     error_handler=self.on_error, timeout=200)

    def on_error(self, _obj, result, _user_data):
        self.error_handler(result)
        GLib.timeout_add(1000, self.service.disconnect, self.port)

    def on_connected(self, _obj, result, _user_data):
        self.reply_handler(self.port)
        self.Applet.Plugins.Run("on_ppp_connected", self.service.device, self.port, result)

        msg = _("Successfully connected to <b>DUN</b> service on <b>%(0)s.</b>\n"
                "Network is now available through <b>%(1)s</b>") % {"0": self.service.device['Alias'], "1": result}

        Notification(_("Connected"), msg, icon_name="network-wireless").show()


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
        if DIALUP_NET_SVCLASS_ID == service.short_uuid:
            def local_reply(port):
                Connection(self.Applet, service, port, reply, err)

            service.connect(reply_handler=local_reply, error_handler=err)
            logging.info("Connecting rfcomm device")

            return True
        else:
            return False
