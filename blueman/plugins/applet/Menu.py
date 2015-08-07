from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from operator import itemgetter

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk


class Menu(AppletPlugin):
    __depends__ = ["StatusIcon"]
    __description__ = _("Provides a menu for the applet and an API for other plugins to manipulate it")
    __icon__ = "menu-editor"
    __author__ = "Walmis"
    __unloadable__ = False

    def on_load(self, applet):
        self.Applet = applet

        self.Applet.Plugins.StatusIcon.connect("popup-menu", self.on_popup_menu)

        self.__plugins_loaded = False

        self.__menuitems = []
        self.__menu = Gtk.Menu()

    def on_popup_menu(self, status_icon, button, activate_time):
        self.__menu.popup(None, None, Gtk.StatusIcon.position_menu,
                          status_icon, button, activate_time)

    def __sort(self):
        self.__menuitems.sort(key=itemgetter(0))

    def __clear(self):
        def each(child, _):
            self.__menu.remove(child)

        self.__menu.foreach(each, None)

    def __load_items(self):
        for item in self.__menuitems:
            self.__menu.append(item[1])
            if item[2]:
                item[1].show()

    def Register(self, owner, item, priority, show=True):
        self.__menuitems.append((priority, item, show, owner))
        if self.__plugins_loaded:
            self.__sort()
            self.__clear()
            self.__load_items()


    def Unregister(self, owner):
        for i in reversed(self.__menuitems):
            priority, item, show, orig_owner = i
            if orig_owner == owner:
                self.__menu.remove(item)
                self.__menuitems.remove(i)

    def on_plugins_loaded(self):
        self.__plugins_loaded = True
        self.__sort()
        self.__load_items()

    def get_menu(self):
        return self.__menu
