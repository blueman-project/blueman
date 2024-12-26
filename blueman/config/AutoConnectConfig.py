from blueman.bluez.BtAddress import BtAddress  # Corrected import for BtAddress
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio
from typing import Tuple


class AutoConnectConfig(Gio.Settings):
    def __init__(self) -> None:
        super().__init__(schema_id="org.blueman.plugins.autoconnect")

    def bind_to_menuitem(self, item: Gtk.CheckMenuItem, data: Tuple[BtAddress, str]) -> None:
        def switch(active: bool) -> None:
            services = set(self.get_value("services"))
            if active:
                services.add(data)
            else:
                services.discard(data)
            self.set_value("services", Gio.Variant("as", list(services)))

        def on_change(config: Gio.Settings, key: str) -> None:
            if key == "services":
                item.props.active = data in set(config.get_value("services"))

        # Initialize the menu item's active state
        item.props.active = data in set(self.get_value("services"))
        item.connect("toggled", lambda i: switch(i.props.active))
        self.connect("changed::services", on_change)
