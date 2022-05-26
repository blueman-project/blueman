from typing import Tuple, Callable, Set, Any, TYPE_CHECKING

from blueman.plugins.BasePlugin import BasePlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from blueman.main.Applet import BluemanApplet


class AppletPlugin(BasePlugin):
    __icon__ = "application-x-addon-symbolic"

    def __init__(self, parent: "BluemanApplet"):
        super().__init__()
        self.parent = parent

        if not Gtk.IconTheme.get_default().has_icon(self.__class__.__icon__):
            self.__class__.__icon__ = "application-x-addon-symbolic"

        self._dbus_service = parent.DbusSvc
        self._dbus_methods: Set[str] = set()
        self._dbus_signals: Set[str] = set()

    def _add_dbus_method(self, name: str, arguments: Tuple[str, ...], return_value: str, method: Callable[..., Any],
                         is_async: bool = False) -> None:
        self._dbus_methods.add(name)
        self._dbus_service.add_method(name, arguments, return_value, method, is_async=is_async)

    def _add_dbus_signal(self, name: str, signature: str) -> None:
        self._dbus_signals.add(name)
        self._dbus_service.add_signal(name, signature)

    def _emit_dbus_signal(self, name: str, *args: Any) -> None:
        self._dbus_service.emit_signal(name, *args)

    def on_unload(self) -> None:
        pass

    def _unload(self) -> None:
        super()._unload()

        for method in self._dbus_methods:
            self._dbus_service.remove_method(method)
        for signal in self._dbus_signals:
            self._dbus_service.remove_signal(signal)

    def _load(self) -> None:
        super()._load()

        # The applet will run on_manager_state_changed once at startup so until it has we don't.
        if self.parent.plugin_run_state_changed:
            self.on_manager_state_changed(self.parent.manager_state)

    # virtual funcs
    def on_manager_state_changed(self, state: bool) -> None:
        """Run when the dbus service appears and disappears. Should only be used to setup, register agents etc"""
        pass

    def on_adapter_added(self, path: str) -> None:
        """Run when a new adapter is added to the system"""
        pass

    def on_adapter_removed(self, path: str) -> None:
        """Run when an adapter is removed from the system"""
        pass

    def on_device_created(self, path: str) -> None:
        """Run when a new device is found"""
        pass

    def on_device_removed(self, path: str) -> None:
        """Run when a device is removed"""
        pass

    def on_adapter_property_changed(self, path: str, key: str, value: Any) -> None:
        """Run when a property changes of any adapters. Make sure to distinguish your actions by path"""
        pass

    def on_device_property_changed(self, path: str, key: str, value: Any) -> None:
        """Run when a property changes of any devices. Make sure to distinguish your actions by path"""
        pass

    # notify when all plugins finished loading
    def on_plugins_loaded(self) -> None:
        pass
