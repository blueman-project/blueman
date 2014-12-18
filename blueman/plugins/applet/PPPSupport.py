from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.main.Mechanism import Mechanism
from blueman.main.Config import Config

from gi.repository import GObject

from blueman.Sdp import *
import os


class Connection:
    def __init__(self, applet, device, port, ok, err):
        self.reply_handler = ok
        self.error_handler = err
        self.device = device
        self.port = port
        self.Applet = applet

        res = os.popen("ps x -o pid,args | grep modem-manager").read()
        if not res:
            self.connect()
        else:
            dprint("ModemManager is running, delaying connection 5sec for it to complete probing")
            GObject.timeout_add(5000, self.connect)

    def connect(self):
        c = Config("gsm_settings/" + self.device.Address)
        if c.props.apn is None:
            c.props.apn = ""

        if c.props.number is None:
            c.props.number = "*99#"

        m = Mechanism()
        m.PPPConnect(self.port, c.props.number, c.props.apn, reply_handler=self.on_connected,
                     error_handler=self.on_error, timeout=200)

    def on_error(self, error):
        self.error_handler(error)
        GObject.timeout_add(1000, self.device.Services["serial"].Disconnect, self.port)

    def on_connected(self, iface):
        self.reply_handler(self.port)
        self.Applet.Plugins.Run("on_ppp_connected", self.device, self.port, iface)

        msg = _("Successfully connected to <b>DUN</b> service on <b>%(0)s.</b>\n"
                "Network is now available through <b>%(1)s</b>") % {"0": self.device.Alias, "1": iface}

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

    def on_rfcomm_connected(self, device, port, uuid):
        pass

    def rfcomm_connect_handler(self, device, uuid, reply, err):
        uuid16 = sdp_get_serial_type(device.Address, uuid)
        if DIALUP_NET_SVCLASS_ID in uuid16:

            def local_reply(port):
                Connection(self.Applet, device, port, reply, err)

            device.Services["serial"].Connect(uuid, reply_handler=local_reply, error_handler=err)
            dprint("Connecting rfcomm device")

            return True
        else:
            return False
