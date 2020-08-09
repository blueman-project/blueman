from gettext import gettext as _
from typing import Callable, Union

from gi.repository import GLib

from blueman.Service import Service
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.NetworkManager import NMDUNConnection, NMConnectionError
from blueman.Sdp import DIALUP_NET_SVCLASS_ID
from blueman.plugins.applet.DBusService import ServiceConnectHandler


class NMDUNSupport(AppletPlugin, ServiceConnectHandler):
    __depends__ = ["StatusIcon", "DBusService"]
    __conflicts__ = ["PPPSupport"]
    __icon__ = "modem"
    __author__ = "infirit"
    __description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager")
    __priority__ = 1

    def service_connect_handler(self, service: Service, ok: Callable[[], None],
                                err: Callable[[Union[NMConnectionError, GLib.Error]], None]) -> bool:
        if DIALUP_NET_SVCLASS_ID != service.short_uuid:
            return False

        conn = NMDUNConnection(service, ok, err)
        conn.activate()

        return True

    def service_disconnect_handler(self, service: Service, ok: Callable[[], None],
                                   err: Callable[[Union[NMConnectionError, GLib.Error]], None]) -> bool:
        if DIALUP_NET_SVCLASS_ID != service.short_uuid:
            return False

        conn = NMDUNConnection(service, ok, err)
        conn.deactivate()

        return True
