from gettext import gettext as _
from typing import Dict

from gi.repository import GLib

from blueman.main.Config import Config
from blueman.bluez.NetworkServer import NetworkServer
from blueman.main.DBusProxies import Mechanism

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.CommonUi import ErrorDialog
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

        self.load_nap_settings()

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self.update_status()

    def load_nap_settings(self) -> None:
        logging.info("Loading NAP settings")

        def reply(_obj: Mechanism, _result: None, _user_data: None) -> None:
            pass

        def err(_obj: Mechanism, result: GLib.Error, _user_data: None) -> None:
            d = ErrorDialog("<b>Failed to apply network settings</b>",
                            "You might not be able to connect to the Bluetooth network via this machine",
                            result,
                            margin_left=9)

            d.run()
            d.destroy()

        m = Mechanism()
        m.ReloadNetwork(result_handler=reply, error_handler=err)

    def on_unload(self) -> None:
        for adapter_path in self._registered:
            s = NetworkServer(obj_path=adapter_path)
            s.unregister("nap")

        self._registered = {}
        del self.Config

    def on_adapter_added(self, path: str) -> None:
        self.update_status()

    def update_status(self) -> None:
        self.set_nap(self.Config["nap-enable"])

    def on_config_changed(self, config: Config, key: str) -> None:
        if key == "nap-enable":
            self.set_nap(config[key])

    def set_nap(self, on: bool) -> None:
        logging.info("set nap %s" % on)
        if self.parent.manager_state:
            adapters = self.parent.Manager.get_adapters()
            for adapter in adapters:
                object_path = adapter.get_object_path()

                registered = self._registered.setdefault(object_path, False)

                s = NetworkServer(obj_path=object_path)
                if on and not registered:
                    s.register("nap", "pan1")
                    self._registered[object_path] = True
                elif not on and registered:
                    s.unregister("nap")
                    self._registered[object_path] = False
