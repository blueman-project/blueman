# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from blueman.plugins.ConfigurablePlugin import ConfigurablePlugin
from functools import partial

ictheme = Gtk.IconTheme.get_default()


class MethodAlreadyExists(Exception):
    pass


class AppletPlugin(ConfigurablePlugin):
    __icon__ = "blueman-plugin"

    def __init__(self, applet):
        super(AppletPlugin, self).__init__(applet)

        if not ictheme.has_icon(self.__class__.__icon__):
            self.__class__.__icon__ = "blueman-plugin"

        self.__opts = {}

        self.Applet = applet

        self.__overrides = []

    def override_method(self, obj, method, override):
        """Replace a method on an object with another which will be called instead"""
        orig = obj.__getattribute__(method)
        obj.__setattr__(method, partial(override, obj))
        self.__overrides.append((obj, method, orig))

    def _unload(self):
        for (obj, method, orig) in self.__overrides:
            obj.__setattr__(method, orig)

        super(AppletPlugin, self)._unload()

        self.Applet.DbusSvc.remove_definitions(self)

    def _load(self, applet):
        super(AppletPlugin, self)._load(applet)

        self.Applet.DbusSvc.add_definitions(self)

        # The applet will run on_manager_state_changed once at startup so until it has we don't.
        if applet.plugin_run_state_changed:
            self.on_manager_state_changed(applet.manager_state)

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

    #notify when all plugins finished loading
    def on_plugins_loaded(self):
        pass
