# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.NetworkManager import NMPANConnection


class NMPANSupport(AppletPlugin):
    __depends__ = ["DBusService"]
    __conflicts__ = ["DhcpClient"]
    __icon__ = "network-workgroup"
    __author__ = "infirit"
    __description__ = _("Provides support for Personal Area Networking (PAN) introduced in NetworkManager 0.8")
    __priority__ = 2

    def on_load(self):
        pass

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
