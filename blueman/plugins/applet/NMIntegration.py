from blueman.Functions import *
from blueman.Constants import HAL_ENABLED
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.Mechanism import Mechanism
from blueman.gui.Notification import Notification
from blueman.Sdp import *
from blueman.bluez.Network import Network

from blueman.main.SignalTracker import SignalTracker

import blueman.bluez as Bluez

from gi.repository import GObject, Gio, Gtk

if not HAL_ENABLED:
    raise ImportError("NMIntegration (deprecated) requires hal support")


class NMIntegration(AppletPlugin):
    __description__ = _("<b>Deprecated</b>\nMakes DUN/PAN connections available for NetworkManager 0.7")
    __icon__ = "modem"
    __depends__ = ["DBusService"]
    __conflicts__ = ["PPPSupport", "DhcpClient"]
    __author__ = "Walmis"
    if HAL_ENABLED:
        __priority__ = 2

    def on_load(self, applet):
        self.Signals = SignalTracker()

        self.Signals.Handle('bluez', Network(), self.on_network_prop_changed, 'PropertyChanged', path_keyword='path')

    def on_unload(self):
        self.Signals.DisconnectAll()

    def on_network_prop_changed(self, key, value, path):
        if key == "Interface":
            if value != "":
                m = Mechanism()
                m.HalRegisterNetDev(value)

    #in: bluez_device_path, rfcomm_device
    #@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="ss", out_signature="")
    def RegisterModem(self, device_path, rfcomm_device):
        dev = Bluez.Device(device_path)
        props = dev.get_properties()

        m = Mechanism()

        def reply():
            dprint("Registered modem")

        def err(excp):
            d = Gtk.MessageDialog(None, type=Gtk.MessageType.WARNING)
            d.props.icon_name = "blueman"
            d.props.text = _("CDMA or GSM not supported")
            d.props.secondary_text = _(
                "The device %s does not appear to support GSM/CDMA.\nThis connection will not work.") % props["Alias"]

            d.add_button(Gtk.STOCK_OK, Gtk.ResponseType.NO)
            resp = d.run()
            d.destroy()

        m.HalRegisterModemPort(rfcomm_device, props["Address"], reply_handler=reply, error_handler=err)


    #in: bluez_device_path, rfcomm_device
    #@dbus.service.method(dbus_interface='org.blueman.Applet', in_signature="s", out_signature="")
    def UnregisterModem(self, device):
        m = Mechanism()
        m.HalUnregisterModemPortDev(device)

        dprint("Unregistered modem")

    def on_rfcomm_connected(self, device, port, uuid):
        signals = SignalTracker()

        def modem_added(mon, udi, address):
            if device.Address == address:
                dprint(udi)
                device.udi = udi

        def modem_removed(mon, udi):
            if device.udi == udi:
                dprint(udi)
                signals.DisconnectAll()

        def disconnected(mon, udi):
            device.Services["serial"].Disconnect(port)
            self.UnregisterModem(port)

        def device_propery_changed(key, value):
            if key == "Connected" and not value:
                self.UnregisterModem(port)


        uuid16 = sdp_get_serial_type(device.Address, uuid)
        if DIALUP_NET_SVCLASS_ID in uuid16:
            try:
                signals.Handle(self.Applet.Plugins.NMMonitor, "modem-added", modem_added)
                signals.Handle(self.Applet.Plugins.NMMonitor, "modem-removed", modem_removed)
                signals.Handle(self.Applet.Plugins.NMMonitor, "disconnected", disconnected)
            except KeyError:
                pass

            signals.Handle("bluez", device.Device, device_propery_changed, "PropertyChanged")
            self.RegisterModem(device.get_object_path(), port)

    def rfcomm_connect_handler(self, device, uuid, reply_handler, error_handler):
        uuid16 = sdp_get_serial_type(device.Address, uuid)
        if DIALUP_NET_SVCLASS_ID in uuid16:
            device.Services["serial"].Connect(uuid, reply_handler=reply_handler, error_handler=error_handler)
            return True
        else:
            return False


    def on_rfcomm_disconnect(self, port):
        self.UnregisterModem(port)
