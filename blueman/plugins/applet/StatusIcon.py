from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.PluginManager import StopException
from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import GObject


class StatusIcon(AppletPlugin, Gtk.StatusIcon):
    __unloadable__ = False
    __icon__ = "blueman-tray"

    FORCE_SHOW = 2
    SHOW = 1
    FORCE_HIDE = 0

    def on_load(self, applet):
        GObject.GObject.__init__(self)
        self.lines = {}
        self.pixbuf = None
        self.timeout = None

        #self.connect("size-changed", self.on_status_icon_resized)

        self.SetTextLine(0, _("Bluetooth Enabled"))

        AppletPlugin.add_method(self.on_query_status_icon_visibility)
        AppletPlugin.add_method(self.on_status_icon_query_icon)

        ic = Gtk.IconTheme.get_default()
        ic.connect("changed", self.on_icon_theme_changed)

        self.on_status_icon_resized()

    def on_icon_theme_changed(self, icon_theme):
        self.IconShouldChange()

    def on_power_state_changed(self, manager, state):
        if state:
            self.SetTextLine(0, _("Bluetooth Enabled"))
        else:
            self.SetTextLine(0, _("Bluetooth Disabled"))

        self.QueryVisibility()

    def QueryVisibility(self):

        rets = self.Applet.Plugins.Run("on_query_status_icon_visibility")
        if not StatusIcon.FORCE_HIDE in rets:
            if StatusIcon.FORCE_SHOW in rets:
                self.set_visible(True)
            else:
                if not self.Applet.Manager:
                    self.set_visible(False)
                    return

                try:
                    self.set_visible(self.Applet.Manager.list_adapters())
                except:
                    self.set_visible(False)
        else:
            self.set_visible(False)

    def set_visible(self, visible):
        self.props.visible = visible

    def SetTextLine(self, id, text):
        if text:
            self.lines[id] = text
        else:
            try:
                del self.lines[id]
            except:
                pass

        self.update_tooltip()


    def update_tooltip(self):
        s = ""
        keys = list(self.lines.keys())
        keys.sort()
        for k in keys:
            s += self.lines[k] + "\n"

        self.props.tooltip_markup = s[:-1]

    def IconShouldChange(self):
        self.on_status_icon_resized()

    def on_adapter_added(self, path):
        self.QueryVisibility()

    def on_adapter_removed(self, path):
        self.QueryVisibility()

    def on_manager_state_changed(self, state):
        self.QueryVisibility()

    def on_status_icon_resized(self):
        self.icon = "blueman-tray"

        ic = Gtk.IconTheme.get_default()

        def callback(inst, ret):
            if ret != None:
                for i in ret:
                    if ic.has_icon(i):
                        self.icon = i
                        raise StopException

        self.Applet.Plugins.RunEx("on_status_icon_query_icon", callback)
        self.props.icon_name = self.icon

        return True

    def on_query_status_icon_visibility(self):
        return StatusIcon.SHOW

    def on_status_icon_query_icon(self):
        return None

