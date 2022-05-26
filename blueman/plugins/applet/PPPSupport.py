from gettext import gettext as _
from typing import TYPE_CHECKING, Callable, Union

from _blueman import RFCOMMError
from blueman.services.meta.SerialService import SerialService

from blueman.bluez.Device import Device
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Notification import Notification
from blueman.main.DBusProxies import Mechanism
from blueman.main.Config import Config

from gi.repository import GLib

import subprocess
import logging

from blueman.plugins.applet.DBusService import RFCOMMConnectHandler
from blueman.services import DialupNetwork

if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class PPPConnectedListener:
    def on_ppp_connected(self, device: Device, rfcomm: str, ppp_port: str) -> None:
        ...


class Connection:
    def __init__(self, applet: "BluemanApplet", service: DialupNetwork, port: int,
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

    def connect(self) -> bool:
        c = Config("org.blueman.gsmsetting", f"/org/blueman/gsmsettings/{self.service.device['Address']}/")

        m = Mechanism()
        m.PPPConnect('(uss)', self.port, c["number"], c["apn"], result_handler=self.on_connected,
                     error_handler=self.on_error)

        return False

    def on_error(self, _obj: Mechanism, result: GLib.Error, _user_data: None) -> None:
        logging.info(f"Failed {result}")
        self.error_handler(result)

        def _connect() -> bool:
            self.service.disconnect(self.port)
            return False

        GLib.timeout_add(1000, _connect)

    def on_connected(self, _obj: Mechanism, result: str, _user_data: None) -> None:
        rfcomm_dev = f"/dev/rfcomm{self.port:d}"
        self.reply_handler(rfcomm_dev)
        for plugin in self.parent.Plugins.get_loaded_plugins(PPPConnectedListener):
            plugin.on_ppp_connected(self.service.device, rfcomm_dev, result)

        msg = _("Successfully connected to <b>DUN</b> service on <b>%(0)s.</b>\n"
                "Network is now available through <b>%(1)s</b>") % {"0": self.service.device['Alias'], "1": result}

        Notification(_("Connected"), msg, icon_name="network-wireless-symbolic").show()


class PPPSupport(AppletPlugin, RFCOMMConnectHandler):
    __depends__ = ["DBusService"]
    __description__ = _("Provides basic support for connecting to the internet via DUN profile.")
    __author__ = "Walmis"
    __icon__ = "modem-symbolic"
    __priority__ = 0

    def rfcomm_connect_handler(self, service: SerialService, reply: Callable[[str], None],
                               err: Callable[[Union[RFCOMMError, GLib.Error]], None]) -> bool:
        if isinstance(service, DialupNetwork):
            def local_reply(port: int) -> None:
                assert isinstance(service, DialupNetwork)  # https://github.com/python/mypy/issues/2608
                Connection(self.parent, service, port, reply, err)

            service.connect(reply_handler=local_reply, error_handler=err)
            logging.info("Connecting rfcomm device")

            return True
        else:
            return False
