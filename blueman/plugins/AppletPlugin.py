from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import GObject

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import inspect
import traceback

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
        self._applet = applet

        self.__overrides = []

    def override_method(self, object, method, override):
        orig = object.__getattribute__(method)
        object.__setattr__(method, partial(override, object))
        self.__overrides.append((object, method, orig))

    def _unload(self):
        for (object, method, orig) in self.__overrides:
            object.__setattr__(method, orig)

        super(AppletPlugin, self)._unload()

        self.Applet.DbusSvc.remove_definitions(self)

    def _load(self, applet):
        super(AppletPlugin, self)._load(applet)

        self.Applet.DbusSvc.add_definitions(self)

        self.on_manager_state_changed(applet.Manager != None)

    # virtual funcs
    def on_manager_state_changed(self, state):
        pass

    def on_adapter_added(self, adapter):
        pass

    def on_adapter_removed(self, adapter):
        pass

    def on_adapter_property_changed(self, path, key, value):
        pass

    #notify when all plugins finished loading
    def on_plugins_loaded(self):
        pass
