from blueman.bluez.BtAddress import BtAddress  # Corrected import for BtAddress
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class AutoConnectConfig(Gio.Settings):
    def __init__(self) -> None:
        super().__init__(schema_id="org.blueman.plugins.autoconnect")

    def bind_to_menuitem(self, item: Gtk.CheckMenuItem, data: tuple[BtAddress, str]) -> None:
        def switch(active: bool) -> None:
            services = set(self["services"])
            if active:
                self["services"] = list(services.union({data}))
            else:
                self["services"] = list(services.difference({data}))

        def on_change(config: AutoConnectConfig, key: str) -> None:
            if key == "services":
                item.props.active = data in set(config["services"])

        item.props.active = data in set(self["services"])
        item.connect("toggled", lambda i: switch(i.props.active))
        self.connect("changed", on_change)
