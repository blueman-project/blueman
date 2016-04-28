# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.main.Config import Config
from blueman.bluez.NetworkServer import NetworkServer
from blueman.main.Mechanism import Mechanism

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.Dialogs import NetworkErrorDialog


class Networking(AppletPlugin):
    __icon__ = "network"
    __description__ = _("Manages local network services, like NAP bridges")
    __author__ = "Walmis"

    _signal = None

    def on_load(self, applet):
        self._registered = {}

        self.Applet = applet

        self.Config = Config("org.blueman.network")
        self.Config.connect("changed", self.on_config_changed)

        self.load_nap_settings()

    def on_manager_state_changed(self, state):
        if state:
            self.update_status()

    def load_nap_settings(self):
        dprint("Loading NAP settings")

        def reply():
            pass

        def err(excp):
            d = NetworkErrorDialog(excp, "You might not be able to connect to the Bluetooth network via this machine")
            d.expander.props.margin_left = 9

            d.run()
            d.destroy()

        m = Mechanism()
        m.ReloadNetwork(reply_handler=reply, error_handler=err)

    def on_unload(self):
        del self.Config

    def on_adapter_added(self, path):
        self.update_status()

    def update_status(self):
        self.set_nap(self.Config["nap-enable"])

    def on_config_changed(self, config, key):
        if key == "nap-enable":
            self.set_nap(config[key])

    def set_nap(self, on):
        dprint("set nap", on)
        if self.Applet.Manager is not None:
            adapters = self.Applet.Manager.list_adapters()
            for adapter in adapters:
                object_path = adapter.get_object_path()

                registered = self._registered.setdefault(object_path, False)

                s = NetworkServer(object_path)
                if on and not registered:
                    s.register("nap", "pan1")
                    self._registered[object_path] = True
                elif not on and registered:
                    s.unregister("nap")
                    self._registered[object_path] = False
