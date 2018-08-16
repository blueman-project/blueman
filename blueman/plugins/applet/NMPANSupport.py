from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.NetworkManager import NMPANConnection


class NMPANSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __conflicts__ = ["DhcpClient"]
    __icon__ = "network"
    __author__ = "Walmis"
    __description__ = _("Provides support for Personal Area Networking (PAN) introduced in NetworkManager 0.8")
    __priority__ = 2

    def on_load(self, applet):
        pass

    @staticmethod
    def service_connect_handler(service, ok, err):
        if service.group != 'network':
            return False

        conn = NMPANConnection(service, ok, err)
        conn.activate()

        return True

    @staticmethod
    def service_connect_handler(service, ok, err):
        if service.group != 'network':
            return False

        conn = NMPANConnection(service, ok, err)
        conn.activate()

        return True

    @staticmethod
    def service_disconnect_handler(service, ok, err):
        if service.group != 'network':
            return False

        conn = NMPANConnection(service, ok, err)
        conn.deactivate()

        return True
