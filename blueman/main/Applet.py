# coding=utf-8
from blueman.Functions import *
import blueman.bluez as bluez
import blueman.plugins.applet
from blueman.main.PluginManager import PersistentPluginManager
from blueman.main.DbusService import DbusService
from blueman.plugins.AppletPlugin import AppletPlugin
import logging

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class BluemanApplet(object):
    def __init__(self):
        setup_icon_path()

        check_single_instance("blueman-applet")

        self.plugin_run_state_changed = False

        self.Manager = bluez.Manager()
        self.Manager.connect_signal('adapter-added', self.on_adapter_added)
        self.Manager.connect_signal('adapter-removed', self.on_adapter_removed)
        self.Manager.connect_signal('device-created', self.on_device_created)
        self.Manager.connect_signal('device-removed', self.on_device_removed)

        self.DbusSvc = DbusService("org.blueman.Applet", "/")

        self.Plugins = PersistentPluginManager(AppletPlugin, blueman.plugins.applet, self)
        self.Plugins.load_plugin()

        self.Plugins.run("on_plugins_loaded")

        self.Manager.watch_name_owner(self._on_dbus_name_appeared, self._on_dbus_name_vanished)

        self._any_adapter = bluez.AnyAdapter()
        self._any_adapter.connect_signal('property-changed', self._on_adapter_property_changed)

        self._any_device = bluez.AnyDevice()
        self._any_device.connect_signal('property-changed', self._on_device_property_changed)

        Gtk.main()

    def _on_dbus_name_appeared(self, _connection, name, owner):
        logging.info("%s %s" % (name, owner))
        self.manager_state = True
        self.plugin_run_state_changed = True
        self.Plugins.run("on_manager_state_changed", self.manager_state)

    def _on_dbus_name_vanished(self, _connection, name):
        logging.info(name)
        self.manager_state = False
        self.plugin_run_state_changed = True
        self.Plugins.run("on_manager_state_changed", self.manager_state)

    def _on_adapter_property_changed(self, _adapter, key, value, path):
        self.Plugins.run("on_adapter_property_changed", path, key, value)

    def _on_device_property_changed(self, _device, key, value, path):
        self.Plugins.run("on_device_property_changed", path, key, value)

    def on_adapter_added(self, _manager, path):
        logging.info("Adapter added %s" % path)

        def on_activate():
            logging.info("Adapter activated")
            self.Plugins.run("on_adapter_added", path)

        adapter = bluez.Adapter(path)
        wait_for_adapter(adapter, on_activate)

    def on_adapter_removed(self, _manager, path):
        logging.info("Adapter removed %s" % path)
        self.Plugins.run("on_adapter_removed", path)

    def on_device_created(self, _manager, path):
        logging.info("Device created %s" % path)
        self.Plugins.run("on_device_created", path)

    def on_device_removed(self, _manager, path):
        logging.info("Device removed %s" % path)
        self.Plugins.run("on_device_removed", path)
