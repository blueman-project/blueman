import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gio

from blueman.bluez.Device import Device


class AutoConnectConfig(Gio.Settings):
    def __init__(self) -> None:
        super().__init__(schema_id="org.blueman.plugins.autoconnect")

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
