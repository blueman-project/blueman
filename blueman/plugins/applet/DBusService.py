from blueman.Functions import *
import pickle
import base64
from blueman.main.Config import Config
from blueman.Sdp import parse_sdp_xml, sdp_save
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.BluezAgent import AdapterAgent

from blueman.bluez.Device import Device as BluezDevice
from blueman.main.Device import Device
from blueman.main.applet.BluezAgent import TempAgent
from blueman.bluez.Adapter import Adapter
from blueman.bluez.Serial import Serial

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
        AppletPlugin.add_method(self.on_device_disconnect)

    @dbus.service.method('org.blueman.Applet', in_signature="s", out_signature="", async_callbacks=("ok", "err"))
    def RefreshServices(self, path, ok, err):
        # BlueZ 4 only!
        device = Device(path)

        def reply(svcs):
            try:
                records = parse_sdp_xml(svcs)
                sdp_save(device.Address, records)
            except:
                pass
            ok()

        device.get_interface().DiscoverServices("", reply_handler=reply, error_handler=err)

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryPlugins(self):
        return self.Applet.Plugins.GetLoaded()

    @dbus.service.method('org.blueman.Applet', in_signature="o", out_signature="", async_callbacks=("ok", "err"))
    def DisconnectDevice(self, obj_path, ok, err):
        dev = Device(obj_path)

        self.Applet.Plugins.Run("on_device_disconnect", dev)

        def on_timeout():
            dev.Disconnect(reply_handler=ok, error_handler=err)

        GObject.timeout_add(1000, on_timeout)

    def on_device_disconnect(self, device):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="as")
    def QueryAvailablePlugins(self):
        return self.Applet.Plugins.GetClasses()

    @dbus.service.method('org.blueman.Applet', in_signature="sb", out_signature="")
    def SetPluginConfig(self, plugin, value):
        self.Applet.Plugins.SetConfig(plugin, value)

    def ConnectHelper(self, interface, object_path, _method, args, ok, err):
        bus = dbus.SystemBus()
        service = bus.get_object("org.bluez", object_path)
        method = service.get_dbus_method(_method, interface)

        method(reply_handler=ok, error_handler=err, *args)


    @dbus.service.method('org.blueman.Applet', in_signature="sosas", async_callbacks=("ok", "err"))
    def ServiceProxy(self, interface, object_path, _method, args, ok, err):

        if _method == "Connect":
            dev = Device(object_path)
            try:
                self.Applet.Plugins.RecentConns.notify(dev, interface, args)
            except KeyError:
                dprint("RecentConns plugin is unavailable")

        self.handled = False

        def cb(inst, ret):
            if ret == True:
                self.handled = True
                #stop further execution
                raise StopException

        self.Applet.Plugins.RunEx("service_connect_handler", cb, interface, object_path, _method, args, ok, err)

        if not self.handled:
            self.ConnectHelper(interface, object_path, _method, args, ok, err)

        del self.handled

    def service_connect_handler(self, interface, object_path, _method, args, ok, err):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="ssbu", async_callbacks=("_ok", "err"))
    def CreateDevice(self, adapter_path, address, pair, time, _ok, err):
        # BlueZ 4 only!
        def ok(device):
            path = device.get_object_path()
            _ok(path)
            self.RefreshServices(path, (lambda *args: None), (lambda *args: None))

        if self.Applet.Manager:
            adapter = Adapter(adapter_path)

            if pair:
                agent_path = "/org/blueman/agent/temp/" + address.replace(":", "")
                agent = TempAgent(self.Applet.Plugins.StatusIcon, agent_path, time)
                adapter.create_paired_device(address, agent_path, "DisplayYesNo", error_handler=err,
                                             reply_handler=ok, timeout=120)

            else:
                adapter.create_device(address, error_handler=err, reply_handler=ok, timeout=120)

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

    @dbus.service.method('org.blueman.Applet', in_signature="ss", out_signature="s", async_callbacks=("ok", "err"))
    def RfcommConnect(self, device, uuid, ok, err):
        def reply(rfcomm):
            self.Applet.Plugins.Run("on_rfcomm_connected", dev, rfcomm, uuid)
            ok(rfcomm)

        dev = Device(device)
        try:
            self.Applet.Plugins.RecentConns.notify(dev.Copy(), Serial().get_interface_name(), [uuid])
        except KeyError:
            pass

        rets = self.Applet.Plugins.Run("rfcomm_connect_handler", dev, uuid, reply, err)
        if True in rets:
            pass
        else:
            dprint("No handler registered")
            err(dbus.DBusException(
                "Service not supported\nPossibly the plugin that handles this service is not loaded"))

    def rfcomm_connect_handler(self, device, uuid, reply_handler, error_handler):
        return False

    @dbus.service.method('org.blueman.Applet', in_signature="ss", out_signature="")
    def RfcommDisconnect(self, device, rfdevice):
        dev = Device(BluezDevice(device))
        dev.Services["serial"].Disconnect(rfdevice)

        self.Applet.Plugins.Run("on_rfcomm_disconnect", rfdevice)

        dprint("Disonnecting rfcomm device")

    def on_rfcomm_connected(self, device, port, uuid):
        pass

    def on_rfcomm_disconnect(self, port):
        pass
