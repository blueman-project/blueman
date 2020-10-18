import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from blueman.bluez.Device import Device
from blueman.main.Config import Config


class AutoConnectConfig(Config):
    def __init__(self) -> None:
        super().__init__("org.blueman.plugins.autoconnect")

    def bind_to_menuitem(self, item: Gtk.CheckMenuItem, device: Device, uuid: str) -> None:
        data = device.get_object_path(), uuid

        def switch(active: bool) -> None:
            services = set(self["services"])
            if active:
                self["services"] = set(services).union({data})
            else:
                self["services"] = set(self["services"]).difference({data})

        def on_change(config: AutoConnectConfig, key: str) -> None:
            if key == "services":
                item.props.active = data in set(config[key])

        item.props.active = data in set(self["services"])
        item.connect("toggled", lambda i: switch(i.props.active))
        self.connect("changed", on_change)
