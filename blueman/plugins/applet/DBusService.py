# coding=utf-8
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Device import Device
from blueman.services.Functions import get_service

from gi.repository import GLib
import logging
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

    @dbus_method('org.blueman.Applet', in_signature="o", out_signature="", invocation_keyword="invocation")
    def DisconnectDevice(self, obj_path, invocation):
        dev = Device(obj_path)

        self.Applet.Plugins.Run("on_device_disconnect", dev)

        def on_timeout():
            dev.disconnect(reply_handler=invocation.return_value, error_handler=invocation.return_error)

        GLib.timeout_add(1000, on_timeout)

    def on_device_disconnect(self, device):
        pass

    @dbus_method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryAvailablePlugins(self):
        return self.Applet.Plugins.GetClasses().keys()

    @dbus_method('org.blueman.Applet', in_signature="sb", out_signature="")
    def SetPluginConfig(self, plugin, value):
        self.Applet.Plugins.SetConfig(plugin, value)

    @dbus_method('org.blueman.Applet', in_signature="os", out_signature="", invocation_keyword="invocation")
    def connect_service(self, object_path, uuid, invocation):
        try:
            self.Applet.Plugins.RecentConns
        except KeyError:
            logging.warning("RecentConns plugin is unavailable")
        else:
            self.Applet.Plugins.RecentConns.notify(object_path, uuid)

        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(object_path)
            device.connect(reply_handler=invocation.return_value, error_handler=invocation.return_error)
        else:
            service = get_service(Device(object_path), uuid)

            if service.group == 'serial':
                def reply(rfcomm):
                    self.Applet.Plugins.Run("on_rfcomm_connected", service, rfcomm)
                    invocation.return_value(rfcomm)

                rets = self.Applet.Plugins.Run("rfcomm_connect_handler", service, reply, invocation.return_error)
                if True in rets:
                    pass
                else:
                    logging.info("No handler registered")
                    invocation.return_error(GLib.Error(
                        "Service not supported\nPossibly the plugin that handles this service is not loaded"))
            else:
                def cb(_inst, ret):
                    if ret:
                        raise StopException

                if not self.Applet.Plugins.RunEx("service_connect_handler", cb, service, invocation.return_value,
                                                 invocation.return_error):
                    service.connect(reply_handler=invocation.return_value, error_handler=invocation.return_error)

    @dbus_method('org.blueman.Applet', in_signature="osd", out_signature="", invocation_keyword="invocation")
    def disconnect_service(self, object_path, uuid, port, invocation):
        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(object_path)
            device.disconnect(reply_handler=invocation.return_error, error_handler=invocation.return_error)
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

                if not self.Applet.Plugins.RunEx("service_disconnect_handler", cb, service, invocation.return_value,
                                                 invocation.return_error):
                    service.disconnect(reply_handler=invocation.return_value, error_handler=invocation.return_error)

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
