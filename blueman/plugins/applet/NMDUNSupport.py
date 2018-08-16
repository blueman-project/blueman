# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.NetworkManager import NMDUNConnection
from blueman.Sdp import DIALUP_NET_SVCLASS_ID


class NMDUNSupport(AppletPlugin):
    __depends__ = ["StatusIcon", "DBusService"]
    __conflicts__ = ["PPPSupport"]
    __icon__ = "modem"
    __author__ = "infirit"
    __description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager")
    __priority__ = 1

    def on_load(self):
        pass

    @staticmethod
    def service_connect_handler(service, ok, err):
        if DIALUP_NET_SVCLASS_ID != service.short_uuid:
            return False

        conn = NMDUNConnection(service, ok, err)
        conn.activate()

        return True

    @staticmethod
    def service_disconnect_handler(service, ok, err):
        if DIALUP_NET_SVCLASS_ID != service.short_uuid:
            return False

        conn = NMDUNConnection(service, ok, err)
        conn.deactivate()

        return True
