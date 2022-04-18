from typing import Any

from blueman.Functions import *
from blueman.bluez.Manager import Manager
from blueman.bluez.Adapter import AnyAdapter
from blueman.bluez.Device import AnyDevice
import blueman.plugins.applet
from blueman.main.PluginManager import PersistentPluginManager
from blueman.main.DbusService import DbusService
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gio, GLib
import logging
import signal


class BluemanApplet(Gio.Application):
    def __init__(self) -> None:
        super().__init__(application_id="org.blueman.Applet", flags=Gio.ApplicationFlags.FLAGS_NONE)
        setup_icon_path()

        def do_quit(_: object) -> bool:
            self.quit()
            return False

        s = GLib.unix_signal_source_new(signal.SIGINT)
        s.set_callback(do_quit)
        s.attach()

        self.plugin_run_state_changed = False
        self.manager_state = False
        self._active = False

        self.Manager = Manager()
        self.Manager.connect_signal('adapter-added', self.on_adapter_added)
        self.Manager.connect_signal('adapter-removed', self.on_adapter_removed)
        self.Manager.connect_signal('device-created', self.on_device_created)
        self.Manager.connect_signal('device-removed', self.on_device_removed)

        self.DbusSvc = DbusService("org.blueman.Applet", "org.blueman.Applet", "/org/blueman/Applet",
                                   Gio.BusType.SESSION)
        self.DbusSvc.register()

        self.Plugins = PersistentPluginManager(AppletPlugin, blueman.plugins.applet, self)
        self.Plugins.load_plugin()

        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_plugins_loaded()

        self.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

        self._any_adapter = AnyAdapter()
        self._any_adapter.connect_signal('property-changed', self._on_adapter_property_changed)

        self._any_device = AnyDevice()
        self._any_device.connect_signal('property-changed', self._on_device_property_changed)

    def do_activate(self) -> None:
        if not self._active:
            self.hold()
            self._active = True

    def _on_dbus_name_appeared(self, _connection: Gio.DBusConnection, name: str, owner: str) -> None:
        logging.info(f"{name} {owner}")
        self.manager_state = True
        self.plugin_run_state_changed = True
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_manager_state_changed(self.manager_state)

    def _on_dbus_name_vanished(self, _connection: Gio.DBusConnection, name: str) -> None:
        logging.info(name)
        self.manager_state = False
        self.plugin_run_state_changed = True
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_manager_state_changed(self.manager_state)

    def _on_adapter_property_changed(self, _adapter: AnyAdapter, key: str, value: Any, path: str) -> None:
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_property_changed(path, key, value)

    def _on_device_property_changed(self, _device: AnyDevice, key: str, value: Any, path: str) -> None:
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_property_changed(path, key, value)

    def on_adapter_added(self, _manager: Manager, path: str) -> None:
        logging.info(f"Adapter added {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_added(path)

    def on_adapter_removed(self, _manager: Manager, path: str) -> None:
        logging.info(f"Adapter removed {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_removed(path)

    def on_device_created(self, _manager: Manager, path: str) -> None:
        logging.info(f"Device created {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_created(path)

    def on_device_removed(self, _manager: Manager, path: str) -> None:
        logging.info(f"Device removed {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_removed(path)
