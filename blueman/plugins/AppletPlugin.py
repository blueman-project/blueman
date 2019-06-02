# coding=utf-8
from blueman.plugins.BasePlugin import BasePlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

ictheme = Gtk.IconTheme.get_default()


class AppletPlugin(BasePlugin):
    __icon__ = "blueman-plugin"

    _dbus_methods = None
    _dbus_signals = None

    def __init__(self, parent):
        super().__init__(parent)

        if not ictheme.has_icon(self.__class__.__icon__):
            self.__class__.__icon__ = "blueman-plugin"

        self.__opts = {}

        self.__overrides = []

        self._dbus_service = parent.DbusSvc
        self._dbus_methods = set()
        self._dbus_signals = set()

    def _add_dbus_method(self, name, arguments, return_value, method, is_async=False):
        self._dbus_methods.add(name)
        self._dbus_service.add_method(name, arguments, return_value, method, is_async=is_async)

    def _add_dbus_signal(self, name, signature):
        self._dbus_signals.add(name)
        self._dbus_service.add_signal(name, signature)

    def _emit_dbus_signal(self, name, *args):
        self._dbus_service.emit_signal(name, *args)

    def on_unload(self):
        pass

    def _unload(self):
        for (obj, method, orig) in self.__overrides:
            obj.__setattr__(method, orig)

        super()._unload()

        for method in self._dbus_methods:
            self._dbus_service.remove_method(method)
        for signal in self._dbus_signals:
            self._dbus_service.remove_signal(signal)

    def _load(self):
        super()._load()

        # The applet will run on_manager_state_changed once at startup so until it has we don't.
        if self.parent.plugin_run_state_changed:
            self.on_manager_state_changed(self.parent.manager_state)

    # virtual funcs
    def on_manager_state_changed(self, state):
        """Run when the dbus service appears and disappears. Should only be used to setup, register agents etc"""
        pass

    def on_adapter_added(self, adapter):
        """Run when a new adapter is added to the system"""
        pass

    def on_adapter_removed(self, adapter):
        """Run when an adapter is removed from the system"""
        pass

    def on_device_created(self, device):
        """Run when a new device is found"""
        pass

    def on_device_removed(self, device):
        """Run when a device is removed"""
        pass

    def on_adapter_property_changed(self, path, key, value):
        """Run when a property changes of any adapters. Make sure to distinguish your actions by path"""
        pass

    def on_device_property_changed(self, path, key, value):
        """Run when a property changes of any devices. Make sure to distinguish your actions by path"""
        pass

    # notify when all plugins finished loading
    def on_plugins_loaded(self):
        pass
