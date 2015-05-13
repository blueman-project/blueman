from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
import pickle
import base64
from blueman.Service import Service
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.BluezAgent import AdapterAgent

from blueman.bluez.Device import Device as BluezDevice
from blueman.main.Device import Device
from blueman.main.applet.BluezAgent import TempAgent
from blueman.bluez.Adapter import Adapter

from gi.repository import GObject
from gi.repository import Gtk
import dbus
import dbus.service


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
            dev.Device.disconnect(reply_handler=ok, error_handler=err)

        GObject.timeout_add(1000, on_timeout)

    def on_device_disconnect(self, device):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryAvailablePlugins(self):
        return self.Applet.Plugins.GetClasses()

    @dbus.service.method('org.blueman.Applet', in_signature="sb", out_signature="")
    def SetPluginConfig(self, plugin, value):
        self.Applet.Plugins.SetConfig(plugin, value)

    @dbus.service.method('org.blueman.Applet', in_signature="os", async_callbacks=("ok", "err"))
    def connect_service(self, object_path, uuid, ok, err):
        service = Device(object_path).get_service(uuid)

        try:
            self.Applet.Plugins.RecentConns
        except KeyError:
            dprint("RecentConns plugin is unavailable")
        else:
            self.Applet.Plugins.RecentConns.notify(service)

        if service.group == 'serial':
            def reply(rfcomm):
                self.Applet.Plugins.Run("on_rfcomm_connected", service, rfcomm)
                ok(rfcomm)

            rets = self.Applet.Plugins.Run("rfcomm_connect_handler", service, reply, err)
            if True in rets:
                pass
            else:
                dprint("No handler registered")
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
        service = Device(object_path).get_service(uuid)

        if service.group == 'serial':
            service.disconnect(port)

            self.Applet.Plugins.Run("on_rfcomm_disconnect", port)

            dprint("Disonnecting rfcomm device")
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

    @dbus.service.method('org.blueman.Applet', in_signature="ssbu", async_callbacks=("_ok", "err"))
    def CreateDevice(self, adapter_path, address, pair, time, _ok, err):
        # BlueZ 4 only!
        def ok(device):
            path = device.get_object_path()
            _ok(path)

        if self.Applet.Manager:
            adapter = Adapter(adapter_path)

            if pair:
                agent_path = "/org/blueman/agent/temp/" + address.replace(":", "")
                agent = TempAgent(self.Applet.Plugins.StatusIcon, agent_path, time)
                adapter.create_paired_device(address, agent_path, "KeyboardDisplay", error_handler=err,
                                             reply_handler=ok, timeout=120)

            else:
                adapter.create_device(address, error_handler=err, reply_handler=ok)

        else:
            err()

    @dbus.service.method('org.blueman.Applet', in_signature="ss", async_callbacks=("ok", "err"))
    def CancelDeviceCreation(self, adapter_path, address, ok, err):
        # BlueZ 4 only!
        if self.Applet.Manager:
            adapter = Adapter(adapter_path)

            adapter.get_interface().CancelDeviceCreation(address, error_handler=err, reply_handler=ok)

        else:
            err()

    @dbus.service.method('org.blueman.Applet')
    def open_plugin_dialog(self):
        self.Applet.Plugins.StandardItems.on_plugins(None)

    def rfcomm_connect_handler(self, service, reply_handler, error_handler):
        return False

    def on_rfcomm_connected(self, device, port):
        pass

    def on_rfcomm_disconnect(self, port):
        pass
