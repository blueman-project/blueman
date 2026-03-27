import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gio, GLib, Gtk
import logging
import signal
from typing import Any, cast
from blueman.bluemantyping import ObjectPath

from blueman.Functions import *
from blueman.bluez.Manager import Manager
from blueman.bluez.Adapter import AnyAdapter
from blueman.bluez.Device import AnyDevice
import blueman.plugins.applet
from blueman.main.PluginManager import PersistentPluginManager
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.applet.DBusService import DBusService
from blueman.plugins.applet.Menu import Menu
from blueman.plugins.applet.PowerManager import PowerManager
from blueman.plugins.applet.RecentConns import RecentConns
from blueman.plugins.applet.StandardItems import StandardItems
from blueman.plugins.applet.StatusIcon import StatusIcon


class BluemanApplet(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id="org.blueman.Applet", flags=Gio.ApplicationFlags.FLAGS_NONE)
        setup_icon_path()

        def do_quit(_: object) -> bool:
            self.quit()
            return False

        log_system_info()

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

        self.Plugins = Plugins(self)
        self.Plugins.load_plugin()

        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_plugins_loaded()

        self.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

        self._any_adapter = AnyAdapter()
        self._any_adapter.connect_signal('property-changed', self._on_adapter_property_changed)

        self._any_device = AnyDevice()
        self._any_device.connect_signal('property-changed', self._on_device_property_changed)

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new("Quit", None)
        quit_action.connect("activate", lambda _action, _param: self.quit())
        self.add_action(quit_action)

        self.set_accels_for_action("win.close", ["<Ctrl>w", "Escape"])

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

    def _on_adapter_property_changed(self, _adapter: AnyAdapter, key: str, value: Any, path: ObjectPath) -> None:
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_property_changed(path, key, value)

    def _on_device_property_changed(self, _device: AnyDevice, key: str, value: Any, path: ObjectPath) -> None:
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_property_changed(path, key, value)

    def on_adapter_added(self, _manager: Manager, path: ObjectPath) -> None:
        logging.info(f"Adapter added {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_added(path)

    def on_adapter_removed(self, _manager: Manager, path: ObjectPath) -> None:
        logging.info(f"Adapter removed {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_removed(path)

    def on_device_created(self, _manager: Manager, path: ObjectPath) -> None:
        logging.info(f"Device created {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_created(path)

    def on_device_removed(self, _manager: Manager, path: ObjectPath) -> None:
        logging.info(f"Device removed {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_removed(path)


class Plugins(PersistentPluginManager[AppletPlugin]):
    def __init__(self, applet: BluemanApplet):
        super().__init__(AppletPlugin, blueman.plugins.applet, applet)

    @property
    def DBusService(self) -> DBusService:
        return cast(DBusService, self._plugins["DBusService"])

    @property
    def Menu(self) -> Menu:
        return cast(Menu, self._plugins["Menu"])

    @property
    def PowerManager(self) -> PowerManager:
        return cast(PowerManager, self._plugins["PowerManager"])

    @property
    def RecentConns(self) -> RecentConns:
        return cast(RecentConns, self._plugins["RecentConns"])

    @property
    def StandardItems(self) -> StandardItems:
        return cast(StandardItems, self._plugins["StandardItems"])

    @property
    def StatusIcon(self) -> StatusIcon:
        return cast(StatusIcon, self._plugins["StatusIcon"])
