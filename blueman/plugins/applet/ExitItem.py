# coding=utf-8
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from blueman.plugins.AppletPlugin import AppletPlugin


class ExitItem(AppletPlugin):
    __depends__ = ["Menu"]
    __description__ = _("Adds an exit menu item to quit the applet")
    __author__ = "Walmis"
    __icon__ = "application-exit"

    def on_load(self):
        self.parent.Plugins.Menu.add(self, 100, text="_Exit", icon_name='application-exit', callback=Gtk.main_quit)

    def on_unload(self):
        self.parent.Plugins.Menu.unregister(self)
