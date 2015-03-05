from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
import gettext

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.SignalTracker import SignalTracker

from gi.repository import GObject
from gi.repository import Gtk


class DiscvManager(AppletPlugin):
    __depends__ = ["Menu"]
    __author__ = "Walmis"
    __icon__ = "edit-find"
    __description__ = _(
        "Provides a menu item for making the default adapter temporarily visible when it is set to hidden by default")

    __gsettings__ = {
        "schema": "org.blueman.plugins.discvmanager",
        "path": None
    }
    __options__ = {
        "time": {
            "type": int,
            "default": 60,
            "name": _("Discoverable timeout"),
            "desc": _("Amount of time in seconds discoverable mode will last"),
            "range": (60, 600)
        }
    }

    def on_load(self, applet):
        self.Signals = SignalTracker()

        self.item = create_menuitem(_("_Make Discoverable"), get_icon("edit-find", 16))
        self.item_label = self.item.get_child().get_children()[1]
        applet.Plugins.Menu.Register(self, self.item, 20, False)

        self.Applet = applet
        self.adapter = None
        self.time_left = -1

        self.Signals.Handle(self.item, "activate", self.on_set_discoverable)
        self.item.props.tooltip_text = _("Make the default adapter temporarily visible")

        self.timeout = None

    def on_unload(self):
        self.Applet.Plugins.Menu.Unregister(self)
        del self.item

        if self.timeout:
            GObject.source_remove(self.timeout)

        self.Signals.DisconnectAll()

    def on_manager_state_changed(self, state):
        if state:
            self.init_adapter()
            self.update_menuitems()
        else:
            self.Signals.Disconnect(0)

            self.adapter = None
            self.update_menuitems()

    def on_update(self):
        self.time_left -= 1
        self.item_label.set_text_with_mnemonic(_("Discoverable... %ss") % self.time_left)
        self.item.props.sensitive = False

        return True

    def on_set_discoverable(self, item):
        if self.adapter:
            self.adapter.set("Discoverable", True)
            self.adapter.set("DiscoverableTimeout", self.get_option("time"))

    def init_adapter(self):
        try:
            self.adapter = self.Applet.Manager.get_adapter()
        except:
            self.adapter = None

    def on_adapter_removed(self, path):
        dprint(path)
        if path == self.adapter.get_object_path():
            self.init_adapter()
            self.update_menuitems()

    def on_adapter_property_changed(self, path, key, value):
        if self.adapter and path == self.adapter.get_object_path():
            dprint("prop", key, value)
            if key == "DiscoverableTimeout":
                if value == 0: #always visible
                    if self.timeout != None:
                        GObject.source_remove(self.timeout)
                    self.time_left = -1
                    self.timeout = None
                else:
                    if self.time_left > -1:
                        if self.timeout != None:
                            GObject.source_remove(self.timeout)
                    self.time_left = value

                    self.timeout = GObject.timeout_add(1000, self.on_update)
                    return

            elif (key == "Discoverable" and not value) or (key == "Powered" and not value):
                dprint("Stop")
                if self.timeout != None:
                    GObject.source_remove(self.timeout)
                self.time_left = -1
                self.timeout = None

            self.update_menuitems()

    def update_menuitems(self):
        try:
            props = self.adapter.get_properties()
        except Exception as e:
            dprint("warning: Adapter is None")
            self.item.props.visible = False
        else:
            if (not props["Discoverable"] or props["DiscoverableTimeout"] > 0) and props["Powered"]:

                self.item.props.visible = True
                self.item_label.set_text_with_mnemonic(_("_Make Discoverable"))
                self.item.props.sensitive = True

            else:
                self.item.props.visible = False
