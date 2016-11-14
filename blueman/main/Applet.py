# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
import blueman.bluez as Bluez
import blueman.plugins.applet
from blueman.main.PluginManager import PersistentPluginManager
from blueman.main.DbusService import DbusService
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
gi.require_version("Gtk", "3.0")
try: import __builtin__ as builtins
except ImportError: import builtins

class BluemanApplet(object):
    def __init__(self):
        setup_icon_path()

        check_single_instance("blueman-applet")

        self._signals = []

        self.plugin_run_state_changed = False

        self.Manager = Bluez.Manager()
        self._signals.append(self.Manager.connect_signal('adapter-added', self.on_adapter_added))
        self._signals.append(self.Manager.connect_signal('adapter-removed', self.on_adapter_removed))
        self._signals.append(self.Manager.connect_signal('device-created', self.on_device_created))
        self._signals.append(self.Manager.connect_signal('device-removed', self.on_device_removed))

        self.DbusSvc = DbusService("org.blueman.Applet", "/")

        self.Plugins = PersistentPluginManager(AppletPlugin, blueman.plugins.applet, self)
        self.Plugins.Load()

        self.Plugins.Run("on_plugins_loaded")

        self.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

        self._any_adapter = Bluez.AnyAdapter()
        self._any_adapter.connect_signal('property-changed', self._on_adapter_property_changed)

        self._any_device = Bluez.AnyDevice()
        self._any_device.connect_signal('property-changed', self._on_device_property_changed)

        Gtk.main()

    def _on_dbus_name_appeared(self, _connection, name, owner):
        dprint(name, owner)
        self.manager_state = True
        self.plugin_run_state_changed = True
        self.Plugins.Run("on_manager_state_changed", self.manager_state)

    def _on_dbus_name_vanished(self, _connection, name):
        dprint(name)
        self.manager_state = False
        self.plugin_run_state_changed = True
        self.Plugins.Run("on_manager_state_changed", self.manager_state)

    def _on_adapter_property_changed(self, _adapter, key, value, path):
        self.Plugins.Run("on_adapter_property_changed", path, key, value)

    def _on_device_property_changed(self, _device, key, value, path):
        self.Plugins.Run("on_device_property_changed", path, key, value)

    def on_adapter_added(self, _manager, path):
        dprint("Adapter added ", path)

        def on_activate():
            dprint("Adapter activated")
            self.Plugins.Run("on_adapter_added", path)

        adapter = Bluez.Adapter(path)
        wait_for_adapter(adapter, on_activate)

    def on_adapter_removed(self, _manager, path):
        dprint("Adapter removed ", path)
        self.Plugins.Run("on_adapter_removed", path)

    def on_device_created(self, _manager, path):
        dprint("Device created ", path)
        self.Plugins.Run("on_device_created", path)

    def on_device_removed(self, _manager, path):
        dprint("Device removed ", path)
        self.Plugins.Run("on_device_removed", path)