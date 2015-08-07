from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import launch, create_menuitem, get_icon
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.CommonUi import show_about_dialog
from blueman.gui.applet.PluginDialog import PluginDialog

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GObject
from gi.repository import Gtk


class StandardItems(AppletPlugin):
    __depends__ = ["StatusIcon", "Menu"]
    __unloadable__ = False
    __description__ = _("Adds standard menu items to the status icon menu")
    __author__ = "walmis"

    def on_load(self, applet):
        self.Applet = applet

        applet.Plugins.Menu.Register(self, Gtk.SeparatorMenuItem(), 21)

        self.new_dev = create_menuitem(_("_Setup New Device") + "...", get_icon("document-new", 16))
        self.new_dev.connect("activate", self.on_setup_new)

        self.Applet.Plugins.Menu.Register(self, self.new_dev, 30)

        self.Applet.Plugins.Menu.Register(self, Gtk.SeparatorMenuItem(), 31)

        self.send = create_menuitem(_("Send _Files to Device") + "...", get_icon("blueman-send-file", 16))
        self.send.connect("activate", self.on_send)

        self.Applet.Plugins.Menu.Register(self, self.send, 40)

        self.browse = create_menuitem(_("_Browse Files on Device") + "...", get_icon("document-open", 16))
        self.browse.connect("activate", self.on_browse)

        self.Applet.Plugins.Menu.Register(self, self.browse, 50)

        self.Applet.Plugins.Menu.Register(self, Gtk.SeparatorMenuItem(), 51)

        self.devices = create_menuitem(_("_Devices") + "...", get_icon("blueman", 16))
        self.devices.connect("activate", self.on_devices)

        self.Applet.Plugins.Menu.Register(self, self.devices, 60)

        self.adapters = create_menuitem(_("Adap_ters") + "...", get_icon("blueman-device", 16))
        self.adapters.connect("activate", self.on_adapters)

        self.Applet.Plugins.Menu.Register(self, self.adapters, 70)

        self.services = create_menuitem(_("_Local Services") + "...", get_icon("preferences-desktop", 16))
        self.services.connect("activate", self.on_local_services)

        self.Applet.Plugins.Menu.Register(self, self.services, 80)

        self.Applet.Plugins.Menu.Register(self, Gtk.SeparatorMenuItem(), 81)

        about = create_menuitem("_Help", get_icon('help-about', 16))
        self.Applet.Plugins.Menu.Register(self, about, 90)

        self.plugins = create_menuitem(_("_Plugins"), get_icon("blueman-plugin", 16))
        self.plugins.connect("activate", self.on_plugins)

        self.Applet.Plugins.Menu.Register(self, self.plugins, 85)

        about.connect("activate", self.on_about)

        def on_activate(status_icon):
            self.on_devices(None)


        self.Applet.Plugins.StatusIcon.connect("activate", on_activate)

    def change_sensitivity(self, sensitive):
        try:
            power = self.Applet.Plugins.PowerManager.GetBluetoothStatus()
        except:
            power = True

        sensitive = sensitive and self.Applet.Manager and power
        self.new_dev.props.sensitive = sensitive
        self.send.props.sensitive = sensitive
        self.browse.props.sensitive = sensitive
        self.devices.props.sensitive = sensitive
        self.adapters.props.sensitive = sensitive

    def on_manager_state_changed(self, state):
        self.change_sensitivity(state)

    def on_power_state_changed(self, manager, state):
        self.change_sensitivity(state)


    def on_setup_new(self, menu_item):
        launch("blueman-assistant", None, False, "blueman", _("Bluetooth Assistant"))

    def on_send(self, menu_item):
        launch("blueman-sendto", None, False, "blueman", _("File Sender"))

    def on_browse(self, menu_item):
        launch("blueman-browse", None, False, "blueman", _("File Browser"))

    def on_devices(self, menu_item):
        launch("blueman-manager", None, False, "blueman", _("Device Manager"))

    def on_adapters(self, menu_item):
        launch("blueman-adapters", None, False, "blueman", _("Adapter Preferences"))

    def on_local_services(self, menu_item):
        launch("blueman-services", None, False, "blueman", _("Service Preferences"))

    def on_about(self, menu_item):
        about = show_about_dialog("Blueman " + _("applet"), run=False)

        button = Gtk.Button(_("Plugins"))
        button.set_image(Gtk.Image.new_from_icon_name("blueman-plugin", Gtk.IconSize.BUTTON))
        button.show()

        button.connect("clicked", self.on_plugins)

        about.action_area.pack_start(button, True, True, 0)
        about.action_area.reorder_child(button, 0)

        about.run()
        about.destroy()

    def on_plugins(self, button):
        dialog = PluginDialog(self.Applet)
        dialog.run()
        dialog.destroy()
