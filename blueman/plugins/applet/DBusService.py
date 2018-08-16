# coding=utf-8
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluez.Device import Device
from blueman.services.Functions import get_service

import dbus
import dbus.service
import logging


class DBusService(AppletPlugin):
    __depends__ = ["StatusIcon"]
    __unloadable__ = False
    __description__ = _("Provides DBus API for other Blueman components")
    __author__ = "Walmis"

    def on_load(self):

        AppletPlugin.add_method(self.on_rfcomm_connected)
        AppletPlugin.add_method(self.on_rfcomm_disconnect)
        AppletPlugin.add_method(self.rfcomm_connect_handler)
        AppletPlugin.add_method(self.service_connect_handler)
        AppletPlugin.add_method(self.service_disconnect_handler)

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryPlugins(self):
        return self.parent.Plugins.get_loaded()

    def on_device_disconnect(self, device):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryAvailablePlugins(self):
        return list(self.parent.Plugins.get_classes())

    @dbus.service.method('org.blueman.Applet', in_signature="sb", out_signature="")
    def SetPluginConfig(self, plugin, value):
        self.parent.Plugins.set_config(plugin, value)

    @dbus.service.method('org.blueman.Applet', in_signature="os", async_callbacks=("ok", "err"))
    def connect_service(self, object_path, uuid, ok, err):
        try:
            self.parent.Plugins.RecentConns
        except KeyError:
            logging.warning("RecentConns plugin is unavailable")
        else:
            self.parent.Plugins.RecentConns.notify(object_path, uuid)

        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(object_path)
            device.connect(reply_handler=ok, error_handler=err)
        else:
            def cb(_inst, ret):
                if ret:
                    raise StopException

            service = get_service(Device(object_path), uuid)

            if service.group == 'serial' and 'NMDUNSupport' in self.QueryPlugins():
                self.parent.Plugins.run_ex("service_connect_handler", cb, service, ok, err)
            elif service.group == 'serial' and 'PPPSupport' in self.QueryPlugins():
                def reply(rfcomm):
                    self.parent.Plugins.run("on_rfcomm_connected", service, rfcomm)
                    ok(rfcomm)

                rets = self.parent.Plugins.run("rfcomm_connect_handler", service, reply, err)
                if True in rets:
                    pass
                else:
                    logging.info("No handler registered")
                    err(dbus.DBusException(
                        "Service not supported\nPossibly the plugin that handles this service is not loaded"))
            else:
                if not self.parent.Plugins.run_ex("service_connect_handler", cb, service, ok, err):
                    service.connect(reply_handler=ok, error_handler=err)

    @dbus.service.method('org.blueman.Applet', in_signature="osd", async_callbacks=("ok", "err"))
    def disconnect_service(self, object_path, uuid, port, ok, err):
        if uuid == '00000000-0000-0000-0000-000000000000':
            device = Device(object_path)
            device.disconnect(reply_handler=ok, error_handler=err)
        else:
            def cb(_inst, ret):
                if ret:
                    raise StopException

            service = get_service(Device(object_path), uuid)

            if service.group == 'serial' and 'NMDUNSupport' in self.QueryPlugins():
                self.parent.Plugins.run_ex("service_disconnect_handler", cb, service, ok, err)
            elif service.group == 'serial' and 'PPPSupport' in self.QueryPlugins():
                service.disconnect(port, reply_handler=ok, error_handler=err)

                self.parent.Plugins.run("on_rfcomm_disconnect", port)

                logging.info("Disconnecting rfcomm device")
            else:
                if not self.parent.Plugins.run_ex("service_disconnect_handler", cb, service, ok, err):
                    service.disconnect(reply_handler=ok, error_handler=err)

    def service_connect_handler(self, service, ok, err):
        pass

    def service_disconnect_handler(self, service, ok, err):
        pass

    @dbus.service.method('org.blueman.Applet')
    def open_plugin_dialog(self):
        self.parent.Plugins.StandardItems.on_plugins()

    def rfcomm_connect_handler(self, service, reply_handler, error_handler):
        return False

    def on_rfcomm_connected(self, service, port):
        pass

    def on_rfcomm_disconnect(self, port):
        pass
