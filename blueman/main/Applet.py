from blueman.Functions import *
from blueman.bluez.Manager import Manager
from blueman.bluez.Adapter import AnyAdapter
from blueman.bluez.Device import AnyDevice
import blueman.plugins.applet
from blueman.main.PluginManager import PersistentPluginManager
from blueman.main.DbusService import DbusService
from blueman.plugins.AppletPlugin import AppletPlugin
from gi.repository import Gio
import logging


class BluemanApplet(Gio.Application):
    def __init__(self):
        super().__init__(application_id="org.blueman.Applet", flags=Gio.ApplicationFlags.FLAGS_NONE)
        setup_icon_path()

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

    def do_activate(self):
        if not self._active:
            self.hold()
            self._active = True

    def _on_dbus_name_appeared(self, _connection, name, owner):
        logging.info(f"{name} {owner}")
        self.manager_state = True
        self.plugin_run_state_changed = True
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_manager_state_changed(self.manager_state)

    def _on_dbus_name_vanished(self, _connection, name):
        logging.info(name)
        self.manager_state = False
        self.plugin_run_state_changed = True
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_manager_state_changed(self.manager_state)

    def _on_adapter_property_changed(self, _adapter, key, value, path):
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_property_changed(path, key, value)

    def _on_device_property_changed(self, _device, key, value, path):
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_property_changed(path, key, value)

    def on_adapter_added(self, _manager, path):
        logging.info(f"Adapter added {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_added(path)

    def on_adapter_removed(self, _manager, path):
        logging.info(f"Adapter removed {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_adapter_removed(path)

    def on_device_created(self, _manager, path):
        logging.info(f"Device created {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_created(path)

    def on_device_removed(self, _manager, path):
        logging.info(f"Device removed {path}")
        for plugin in self.Plugins.get_loaded_plugins(AppletPlugin):
            plugin.on_device_removed(path)
