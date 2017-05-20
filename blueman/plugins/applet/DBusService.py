# coding=utf-8
from blueman.Functions import *
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Device import Device
from blueman.services.Functions import get_service

from gi.repository import GLib
import dbus
import dbus.service
import logging


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

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryPlugins(self):
        return self.Applet.Plugins.GetLoaded()

    @dbus.service.method('org.blueman.Applet', in_signature="o", out_signature="", async_callbacks=("ok", "err"))
    def DisconnectDevice(self, obj_path, ok, err):
        dev = Device(obj_path)

        self.Applet.Plugins.Run("on_device_disconnect", dev)

        def on_timeout():
            dev.disconnect(reply_handler=ok, error_handler=err)

        GLib.timeout_add(1000, on_timeout)

    def on_device_disconnect(self, device):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryAvailablePlugins(self):
        return self.Applet.Plugins.GetClasses().keys()

    @dbus.service.method('org.blueman.Applet', in_signature="sb", out_signature="")
    def SetPluginConfig(self, plugin, value):
        self.Applet.Plugins.SetConfig(plugin, value)

    @dbus.service.method('org.blueman.Applet', in_signature="os", async_callbacks=("ok", "err"))
    def connect_service(self, object_path, uuid, ok, err):
        try:
            self.Applet.Plugins.RecentConns
        except KeyError:
            logging.watning("RecentConns plugin is unavailable")
        else:
            self.Applet.Plugins.RecentConns.notify(object_path, uuid)

        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(object_path)
            device.connect(reply_handler=ok, error_handler=err)
        else:
            service = get_service(Device(object_path), uuid)

            if service.group == 'serial':
                def reply(rfcomm):
                    self.Applet.Plugins.Run("on_rfcomm_connected", service, rfcomm)
                    ok(rfcomm)

                rets = self.Applet.Plugins.Run("rfcomm_connect_handler", service, reply, err)
                if True in rets:
                    pass
                else:
                    logging.info("No handler registered")
                    err(dbus.DBusException(
                        "Service not supported\nPossibly the plugin that handles this service is not loaded"))
            else:
                def cb(_inst, ret):
                    if ret:
                        raise StopException

                if not self.Applet.Plugins.RunEx("service_connect_handler", cb, service, ok, err):
                    service.connect(reply_handler=ok, error_handler=err)

    @dbus.service.method('org.blueman.Applet', in_signature="osd", async_callbacks=("ok", "err"))
    def disconnect_service(self, object_path, uuid, port, ok, err):
        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(object_path)
            device.disconnect(reply_handler=ok, error_handler=err)
        else:
            service = get_service(Device(object_path), uuid)

            if service.group == 'serial':
                service.disconnect(port)

                self.Applet.Plugins.Run("on_rfcomm_disconnect", port)

                logging.info("Disonnecting rfcomm device")
            else:

                def cb(_inst, ret):
                    if ret:
                        raise StopException

                if not self.Applet.Plugins.RunEx("service_disconnect_handler", cb, service, ok, err):
                    service.disconnect(reply_handler=ok, error_handler=err)

    def service_connect_handler(self, service, ok, err):
        pass

    def service_disconnect_handler(self, service, ok, err):
        pass

    @dbus.service.method('org.blueman.Applet')
    def open_plugin_dialog(self):
        self.Applet.Plugins.StandardItems.on_plugins(None)

    def rfcomm_connect_handler(self, service, reply_handler, error_handler):
        return False

    def on_rfcomm_connected(self, device, port):
        pass

    def on_rfcomm_disconnect(self, port):
        pass
