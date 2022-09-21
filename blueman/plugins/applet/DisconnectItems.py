from gettext import gettext as _
from typing import Any, TYPE_CHECKING

from blueman.plugins.AppletPlugin import AppletPlugin

if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class DisconnectItems(AppletPlugin):
    __depends__ = ["Menu"]
    __icon__ = "bluetooth-disconnected-symbolic"
    __author__ = "cschramm"
    __description__ = _("Adds disconnect menu items")

    def __init__(self, parent: "BluemanApplet"):
        super().__init__(parent)
        self._menu = self.parent.Plugins.Menu

    def on_unload(self) -> None:
        self._menu.unregister(self)

    def on_manager_state_changed(self, state: bool) -> None:
        self._menu.unregister(self)
        if state:
            self._render()

    def on_adapter_removed(self, path: str) -> None:
        self._menu.unregister(self)
        self._render()

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        if key == "Connected":
            self._menu.unregister(self)
            self._render()

    def _render(self) -> None:
        for idx, device in enumerate(self.parent.Manager.get_devices()):
            if device["Connected"]:
                self._menu.add(self, (25, idx), text=_("Disconnect %s") % device["Alias"],
                               icon_name="bluetooth-disconnected-symbolic",
                               callback=lambda dev=device: dev.disconnect())
