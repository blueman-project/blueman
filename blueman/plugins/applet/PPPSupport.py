# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.main.DBusProxies import Mechanism
from blueman.main.Config import Config

from gi.repository import GLib

from blueman.Sdp import DIALUP_NET_SVCLASS_ID
import subprocess
import logging


class Connection:
    def __init__(self, applet, service, port, ok, err):
        self.reply_handler = ok
        self.error_handler = err
        self.service = service
        self.port = port
        self.parent = applet

        stdout, stderr = subprocess.Popen(['ps', 'ax', '-o', 'pid,args'], stdout=subprocess.PIPE).communicate()
        if b'ModemManager' in stdout:
            timeout = 10
            logging.info("ModemManager is running, delaying connection %ssec for it to complete probing" % timeout)
            GLib.timeout_add_seconds(timeout, self.connect)
        else:
            self.connect()

    def connect(self):
        c = Config("org.blueman.gsmsetting", "/org/blueman/gsmsettings/%s/" % self.service.device['Address'])

        m = Mechanism()
        m.PPPConnect('(sss)', self.port, c["number"], c["apn"], result_handler=self.on_connected,
                     error_handler=self.on_error)

    def on_error(self, _obj, result, _user_data):
        logging.info('Failed %s' % result)
        # FIXME confusingly self.port is the full rfcomm device path but the service expects the number only
        self.error_handler(result)
        GLib.timeout_add(1000, self.service.disconnect, int(self.port[-1]))

    def on_connected(self, _obj, result, _user_data):
        self.reply_handler(self.port)
        self.parent.Plugins.run("on_ppp_connected", self.service.device, self.port, result)

        msg = _("Successfully connected to <b>DUN</b> service on <b>%(0)s.</b>\n"
                "Network is now available through <b>%(1)s</b>") % {"0": self.service.device['Alias'], "1": result}

        Notification(_("Connected"), msg, icon_name="network-wireless").show()


class PPPSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __description__ = _("Provides basic support for connecting to the internet via DUN profile.")
    __author__ = "Walmis"
    __icon__ = "modem"
    __priority__ = 0

    def on_load(self):
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
                Connection(self.parent, service, port, reply, err)

            service.connect(reply_handler=local_reply, error_handler=err)
            logging.info("Connecting rfcomm device")

            return True
        else:
            return False
