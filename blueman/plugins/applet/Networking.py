from blueman.Functions import *
from blueman.Constants import *
from blueman.bluez.NetworkServer import NetworkServer
from blueman.main.Mechanism import Mechanism
from blueman.main.SignalTracker import SignalTracker

from blueman.plugins.AppletPlugin import AppletPlugin

from gi.repository import Gio
import dbus


class Networking(AppletPlugin):
    __icon__ = "network"
    __description__ = _("Manages local network services, like NAP bridges")
    __author__ = "Walmis"

    def on_load(self, applet):
        self.Applet = applet
        self.Signals = SignalTracker()

        self.Settings = Gio.Settings.new(BLUEMAN_NETWORK_GSCHEMA)
        self.Signals.Handle("gobject", self.Settings, "changed", self.on_config_changed)

        self.load_nap_settings()

    def on_manager_state_changed(self, state):
        if state:
            self.update_status()

    def load_nap_settings(self):
        dprint("Loading NAP settings")

        def reply():
            pass

        def err(excp):
            lines = str(excp).splitlines()
            d = Gtk.MessageDialog(None, buttons=Gtk.ButtonsType.OK, type=Gtk.MessageType.ERROR)
            d.props.text = _("Failed to apply network settings")
            d.props.secondary_text = lines[-1] + "\n\n" + _(
                "You might not be able to connect to the Bluetooth network via this machine")
            d.run()
            d.destroy()

        m = Mechanism()
        m.ReloadNetwork(reply_handler=reply, error_handler=err)

    def on_unload(self):
        self.Signals.DisconnectAll()

    def on_adapter_added(self, path):
        self.update_status()

    def update_status(self):
        self.set_nap(self.Settings["nap-enable"])

    def on_config_changed(self, config, key, value):
        if key == "nap-enable":
            self.set_nap(value)

    def set_nap(self, on):
        dprint("set nap", on)
        if self.Applet.Manager != None:
            adapters = self.Applet.Manager.list_adapters()
            for adapter in adapters:
                s = NetworkServer(adapter.get_object_path())
                if on:
                    s.register("nap", "pan1")
                else:
                    s.unregister("nap")
