from gettext import gettext as _
from typing import Any, Optional

from blueman.bluez.Adapter import Adapter
from blueman.bluez.errors import DBusNoSuchAdapterError
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import GLib
import logging


class DiscvManager(AppletPlugin):
    __depends__ = ["Menu"]
    __author__ = "Walmis"
    __icon__ = "edit-find"
    __description__ = _(
        "Provides a menu item for making the default adapter temporarily visible when it is set to hidden by default")

    __gsettings__ = {
        "schema": "org.blueman.plugins.discvmanager",
        "path": None
    }
    __options__ = {
        "time": {
            "type": int,
            "default": 60,
            "name": _("Discoverable timeout"),
            "desc": _("Amount of time in seconds discoverable mode will last"),
            "range": (60, 600)
        }
    }

    adapter: Optional[Adapter]

    def on_load(self) -> None:
        self.item = self.parent.Plugins.Menu.add(self, 20, text=_("_Make Discoverable"), icon_name="edit-find",
                                                 tooltip=_("Make the default adapter temporarily visible"),
                                                 callback=self.on_set_discoverable, visible=False)
        self.adapter = None
        self.time_left = -1

        self.timeout: Optional[int] = None

    def on_unload(self) -> None:
        self.parent.Plugins.Menu.unregister(self)
        del self.item

        if self.timeout:
            GLib.source_remove(self.timeout)

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self.init_adapter()
            self.update_menuitems()
        else:
            self.adapter = None
            self.update_menuitems()

    def on_update(self) -> bool:
        self.time_left -= 1
        self.item.set_text(_("Discoverable… %ss") % self.time_left)
        self.item.set_sensitive(False)

        return True

    def on_set_discoverable(self) -> None:
        if self.adapter:
            self.adapter.set("Discoverable", True)
            self.adapter.set("DiscoverableTimeout", self.get_option("time"))

    def init_adapter(self) -> None:
        try:
            self.adapter = self.parent.Manager.get_adapter()
        except DBusNoSuchAdapterError:
            self.adapter = None

    def on_adapter_added(self, path: str) -> None:
        if self.adapter is None:
            self.init_adapter()
            self.update_menuitems()

    def on_adapter_removed(self, path: str) -> None:
        logging.info(path)
        if self.adapter is None:
            # FIXME we appear to call this more than once on adapter removal
            logging.warning("Warning: adapter is None")
        elif path == self.adapter.get_object_path():
            self.init_adapter()
            self.update_menuitems()

    def on_adapter_property_changed(self, path: str, key: str, value: Any) -> None:
        if self.adapter and path == self.adapter.get_object_path():
            logging.debug(f"prop {key} {value}")
            if key == "DiscoverableTimeout":
                if value == 0:  # always visible
                    if self.timeout is not None:
                        GLib.source_remove(self.timeout)
                    self.time_left = -1
                    self.timeout = None
                else:
                    if self.time_left > -1:
                        if self.timeout is not None:
                            GLib.source_remove(self.timeout)
                    self.time_left = value

                    self.timeout = GLib.timeout_add(1000, self.on_update)
                    return

            elif (key == "Discoverable" and not value) or (key == "Powered" and not value):
                logging.info("Stop")
                if self.timeout is not None:
                    GLib.source_remove(self.timeout)
                self.time_left = -1
                self.timeout = None

            self.update_menuitems()

    def update_menuitems(self) -> None:
        if self.adapter is None:
            logging.warning("warning: Adapter is None")
            self.item.set_visible(False)
        elif (not self.adapter["Discoverable"] or self.adapter["DiscoverableTimeout"] > 0) and self.adapter["Powered"]:
            self.item.set_visible(True)
            self.item.set_text(_("_Make Discoverable"))
            self.item.set_sensitive(True)
        else:
            self.item.set_visible(False)
