from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.Sdp import uuid128_to_uuid16, DIALUP_NET_SVCLASS_ID
from blueman.main.NetworkManager import NMDUNConnection


class NMDUNSupport(AppletPlugin):
    __depends__ = ["StatusIcon", "DBusService"]
    __conflicts__ = ["PPPSupport"]
    __icon__ = "modem"
    __author__ = "infirit"
    __description__ = _("Provides support for Dial Up Networking (DUN) with ModemManager and NetworkManager")
    __priority__ = 1

    def on_load(self, applet):
        pass

    def on_unload(self):
        pass

    @staticmethod
    def service_connect_handler(service, ok, err):
        if DIALUP_NET_SVCLASS_ID != uuid128_to_uuid16(service.uuid):
            return False
        conn = NMDUNConnection(service, ok, err)
        conn.activate()

        return True

    @staticmethod
    def service_disconnect_handler(service, ok, err):
        if DIALUP_NET_SVCLASS_ID != uuid128_to_uuid16(service.uuid):
            return False
        conn = NMDUNConnection(service, ok, err)
        conn.deactivate()

        return True
