# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Device import Device
from blueman.services.Functions import get_service

from gi.repository import GLib
from blueman.main.DBusServiceObject import *

class DBusService(AppletPlugin):
    __depends__ = ["StatusIcon"]
    __unloadable__ = False
    __description__ = _("Provides DBus API for other Blueman components")
    __author__ = "Walmis"

    def on_load(self, applet):
        self.Applet = applet

        AppletPlugin.add_method(self.on_rfcomm_connected)
        AppletPlugin.add_method(self.on_rfcomm_disconnect)
        AppletPlugin.add_method(self.rfcomm_connect_handler)
        AppletPlugin.add_method(self.service_connect_handler)
        AppletPlugin.add_method(self.service_disconnect_handler)
        AppletPlugin.add_method(self.on_device_disconnect)

    @dbus_method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryPlugins(self):
        return self.Applet.Plugins.GetLoaded()

    @dbus_method('org.blueman.Applet', in_signature="o", out_signature="")
    def DisconnectDevice(self, obj_path):
        dev = Device(obj_path)

        self.Applet.Plugins.Run("on_device_disconnect", dev)

        def ok(*args):
            return args
        def err(error):
            raise error

        def on_timeout():
            dev.disconnect(reply_handler=ok, error_handler=err)

        GLib.timeout_add(1000, on_timeout)

    def on_device_disconnect(self, device):
        pass

    @dbus_method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryAvailablePlugins(self):
        return self.Applet.Plugins.GetClasses().keys()

    @dbus_method('org.blueman.Applet', in_signature="sb", out_signature="")
    def SetPluginConfig(self, plugin, value):
        self.Applet.Plugins.SetConfig(plugin, value)

    @dbus_method('org.blueman.Applet', in_signature="os", out_signature="")
    def connect_service(self, object_path, uuid):
        service = get_service(Device(object_path), uuid)

        try:
            self.Applet.Plugins.RecentConns
        except KeyError:
            dprint("RecentConns plugin is unavailable")
        else:
            self.Applet.Plugins.RecentConns.notify(service)

        if service.group == 'serial':
            def reply(rfcomm):
                self.Applet.Plugins.Run("on_rfcomm_connected", service, rfcomm)
                return rfcomm

            def error(error):
                raise error

            rets = self.Applet.Plugins.Run("rfcomm_connect_handler", service, reply, error)
            if True in rets:
                pass
            else:
                dprint("No handler registered")
                error(GLib.Error(
                    "Service not supported\nPossibly the plugin that handles this service is not loaded"))
        else:
            def cb(_inst, ret):
                if ret:
                    raise StopException

            def reply(*args):
                return args
            def error(error):
                raise error

            if not self.Applet.Plugins.RunEx("service_connect_handler", cb, service, reply, error):
                service.connect(reply_handler=reply, error_handler=error)

    @dbus_method('org.blueman.Applet', in_signature="osd", out_signature="")
    def disconnect_service(self, object_path, uuid, port):
        service = get_service(Device(object_path), uuid)

        if service.group == 'serial':
            service.disconnect(port)

            self.Applet.Plugins.Run("on_rfcomm_disconnect", port)

            dprint("Disonnecting rfcomm device")
        else:

            def cb(_inst, ret):
                if ret:
                    raise StopException

            def reply():
                return
            def error(error):
                raise error

            if not self.Applet.Plugins.RunEx("service_disconnect_handler", cb, service, reply, error):
                service.disconnect(reply_handler=reply, error_handler=error)

    def service_connect_handler(self, service, ok, err):
        pass

    def service_disconnect_handler(self, service, ok, err):
        pass

    @dbus_method('org.blueman.Applet')
    def open_plugin_dialog(self):
        self.Applet.Plugins.StandardItems.on_plugins(None)

    def rfcomm_connect_handler(self, service, reply_handler, error_handler):
        return False

    def on_rfcomm_connected(self, device, port):
        pass

    def on_rfcomm_disconnect(self, port):
        pass
