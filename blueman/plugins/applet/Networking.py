from gettext import gettext as _
from typing import Dict

from blueman.main.Config import Config
from blueman.bluez.NetworkServer import NetworkServer
from blueman.main.DBusProxies import Mechanism

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.CommonUi import ErrorDialog
from gi.repository import GLib
import logging


class Networking(AppletPlugin):
    __icon__ = "network-workgroup"
    __description__ = _("Manages local network services, like NAP bridges")
    __author__ = "Walmis"

    _signal = None

    def on_load(self) -> None:
        self._registered: Dict[str, bool] = {}

        self.Config = Config("org.blueman.network")
        self.Config.connect("changed", self.on_config_changed)
        self._mechanism = Mechanism()

        self.set_nap(self.Config['nap-enable'])

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self.set_nap(self.Config["nap-enable"])

    def enable_network(self):
        try:
            self._mechanism.EnableNetwork('(sss)', self.Config['ipaddress'], '255.255.255.0',
                                          self.Config['dhcphandler'])
        except GLib.Error as e:
            # It will error on applet startup anyway so lets make sure to disable
            self.disable_network()
            self.show_error_dialog(e)

    def disable_network(self):
        try:
            self._mechanism.DisableNetwork()
        except GLib.Error as e:
            self.show_error_dialog(e)

    def on_adapter_added(self, path: str) -> None:
        self.set_nap(self.Config["nap-enable"])

    def on_config_changed(self, config: Config, key: str) -> None:
        if key in ('nap-enable', 'ipaddress', 'dhcphandler'):
            self.set_nap(config['nap-enable'])

    def show_error_dialog(self, excp: Exception):
        def run_dialog(dialog):
            dialog.run()
            dialog.destroy()

        d = ErrorDialog('<b>Failed to apply network settings</b>',
                        'You might not be able to connect to the Bluetooth network via this machine',
                        excp, margin_left=9)
        GLib.idle_add(run_dialog, d)

    def set_nap(self, enable):
        logging.info("set nap %s" % enable)
        if self.parent.manager_state:
            adapters = self.parent.Manager.get_adapters()
            for adapter in adapters:
                object_path = adapter.get_object_path()

                registered = self._registered.setdefault(object_path, False)

                s = NetworkServer(obj_path=object_path)
                if enable and not registered:
                    s.register("nap", "pan1")
                    self._registered[object_path] = True
                elif not enable and registered:
                    s.unregister("nap")
                    self._registered[object_path] = False

            if enable:
                self.enable_network()
            else:
                self.disable_network()
