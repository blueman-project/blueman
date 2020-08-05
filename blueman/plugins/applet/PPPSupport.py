from gettext import gettext as _
from typing import TYPE_CHECKING, Callable, Union

from _blueman import RFCOMMError

from blueman.Service import Service
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.main.DBusProxies import Mechanism
from blueman.main.Config import Config

from gi.repository import GLib

import subprocess
import logging

from blueman.services import DialupNetwork

if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class Connection:
    def __init__(self, applet: "BluemanApplet", service: DialupNetwork, port: str,
                 ok: Callable[[str], None], err: Callable[[GLib.Error], None]):
        self.reply_handler = ok
        self.error_handler = err
        self.service = service
        self.port = port
        self.parent = applet

        stdout, stderr = subprocess.Popen(['ps', 'ax', '-o', 'pid,args'], stdout=subprocess.PIPE).communicate()
        if b'ModemManager' in stdout:
            timeout = 10
            logging.info(f"ModemManager is running, delaying connection {timeout} sec for it to complete probing")
            GLib.timeout_add_seconds(timeout, self.connect)
        else:
            self.connect()

    def connect(self):
        c = Config("org.blueman.gsmsetting", f"/org/blueman/gsmsettings/{self.service.device['Address']}/")

        m = Mechanism()
        m.PPPConnect('(sss)', self.port, c["number"], c["apn"], result_handler=self.on_connected,
                     error_handler=self.on_error)

    def on_error(self, _obj: Mechanism, result: GLib.Error, _user_data: None) -> None:
        logging.info(f"Failed {result}")
        # FIXME confusingly self.port is the full rfcomm device path but the service expects the number only
        self.error_handler(result)
        GLib.timeout_add(1000, self.service.disconnect, int(self.port[-1]))

    def on_connected(self, _obj: Mechanism, result: str, _user_data: None) -> None:
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

    def rfcomm_connect_handler(self, service: Service, reply: Callable[[str], None],
                               err: Callable[[Union[RFCOMMError, GLib.Error]], None]) -> bool:
        if isinstance(service, DialupNetwork):
            def local_reply(port: str) -> None:
                assert isinstance(service, DialupNetwork)  # https://github.com/python/mypy/issues/2608
                Connection(self.parent, service, port, reply, err)

            service.connect(reply_handler=local_reply, error_handler=err)
            logging.info("Connecting rfcomm device")

            return True
        else:
            return False
