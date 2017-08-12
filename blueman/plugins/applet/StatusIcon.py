# coding=utf-8

from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class StatusIcon(AppletPlugin, Gtk.StatusIcon):
    __unloadable__ = False
    __icon__ = "blueman-tray"

    FORCE_SHOW = 2
    SHOW = 1
    FORCE_HIDE = 0

    visibility_timeout = None

    def on_load(self, applet):
        Gtk.StatusIcon.__init__(self)
        self.lines = {}

        self.set_title('blueman')

        self.set_text_line(0, _("Bluetooth Enabled"))

        AppletPlugin.add_method(self.on_query_status_icon_visibility)
        AppletPlugin.add_method(self.on_status_icon_query_icon)

        ic = Gtk.IconTheme.get_default()
        ic.connect("changed", self.on_icon_theme_changed)

        self.on_status_icon_resized()

    @property
    def geometry(self):
        _, screen, area, orientation = self.get_geometry()
        return (area.x, area.y, area.width, area.height)

    def on_icon_theme_changed(self, icon_theme):
        self.icon_should_change()

    def on_power_state_changed(self, manager, state):
        if state:
            self.set_text_line(0, _("Bluetooth Enabled"))
            self.query_visibility(delay_hiding=True)
        else:
            self.set_text_line(0, _("Bluetooth Disabled"))
            self.query_visibility()

    def query_visibility(self, delay_hiding=False):
        rets = self.Applet.Plugins.run("on_query_status_icon_visibility")
        if StatusIcon.FORCE_HIDE not in rets:
            if StatusIcon.FORCE_SHOW in rets:
                self.set_visible(True)
            else:
                if not self.Applet.Manager:
                    self.set_visible(False)
                    return

                if self.Applet.Manager.get_adapters():
                    self.set_visible(True)
                elif not self.visibility_timeout:
                    if delay_hiding:
                        self.visibility_timeout = GLib.timeout_add(1000, self.on_visibility_timeout)
                    else:
                        self.set_visible(False)
        else:
            self.set_visible(False)

    def on_visibility_timeout(self):
        GLib.source_remove(self.visibility_timeout)
        self.visibility_timeout = None
        self.query_visibility()

    def set_visible(self, visible):
        self.props.visible = visible

    def set_text_line(self, lineid, text):
        if text:
            self.lines[lineid] = text
        else:
            self.lines.pop(lineid, None)

        self.update_tooltip()

    def update_tooltip(self):
        s = ""
        keys = list(self.lines.keys())
        keys.sort()
        for k in keys:
            s += self.lines[k] + "\n"

        self.props.tooltip_markup = s[:-1]

    def icon_should_change(self):
        self.on_status_icon_resized()

    def on_adapter_added(self, path):
        self.query_visibility()

    def on_adapter_removed(self, path):
        self.query_visibility()

    def on_manager_state_changed(self, state):
        self.query_visibility()

    def on_status_icon_resized(self):
        self.icon = "blueman-tray"

        ic = Gtk.IconTheme.get_default()

        def callback(inst, ret):
            if ret is not None:
                for i in ret:
                    if ic.has_icon(i):
                        self.icon = i
                        raise StopException

        self.Applet.Plugins.run_ex("on_status_icon_query_icon", callback)
        self.props.icon_name = self.icon
        self.query_visibility()

        return True

    def on_query_status_icon_visibility(self):
        return StatusIcon.SHOW

    def on_status_icon_query_icon(self):
        return None
