# coding=utf-8
from blueman.Functions import launch, create_menuitem, get_lockfile, get_pid, is_running, os, signal
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.CommonUi import show_about_dialog
from blueman.gui.applet.PluginDialog import PluginDialog

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class StandardItems(AppletPlugin):
    __depends__ = ["StatusIcon", "Menu"]
    __unloadable__ = False
    __description__ = _("Adds standard menu items to the status icon menu")
    __author__ = "walmis"

    def on_load(self, applet):
        self.Applet = applet

        applet.Plugins.Menu.register(self, Gtk.SeparatorMenuItem(), 21)

        self.new_dev = create_menuitem(_("_Set Up New Device") + "...", "document-new")
        self.new_dev.connect("activate", self.on_setup_new)

        self.Applet.Plugins.Menu.register(self, self.new_dev, 30)

        self.Applet.Plugins.Menu.register(self, Gtk.SeparatorMenuItem(), 31)

        self.send = create_menuitem(_("Send _Files to Device") + "...", "blueman-send-file")
        self.send.connect("activate", self.on_send)

        self.Applet.Plugins.Menu.register(self, self.send, 40)

        self.Applet.Plugins.Menu.register(self, Gtk.SeparatorMenuItem(), 51)

        self.devices = create_menuitem(_("_Devices") + "...", "blueman")
        self.devices.connect("activate", self.on_devices)

        self.Applet.Plugins.Menu.register(self, self.devices, 60)

        self.adapters = create_menuitem(_("Adap_ters") + "...", "blueman-device")
        self.adapters.connect("activate", self.on_adapters)

        self.Applet.Plugins.Menu.register(self, self.adapters, 70)

        self.services = create_menuitem(_("_Local Services") + "...", "preferences-desktop")
        self.services.connect("activate", self.on_local_services)

        self.Applet.Plugins.Menu.register(self, self.services, 80)

        self.Applet.Plugins.Menu.register(self, Gtk.SeparatorMenuItem(), 81)

        about = create_menuitem("_Help", 'help-about')
        self.Applet.Plugins.Menu.register(self, about, 90)

        self.plugins = create_menuitem(_("_Plugins"), "blueman-plugin")
        self.plugins.connect("activate", self.on_plugins)

        self.Applet.Plugins.Menu.register(self, self.plugins, 85)

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

    def on_devices(self, menu_item):
        lockfile = get_lockfile('blueman-manager')
        pid = get_pid(lockfile)
        if lockfile and pid and is_running('blueman-manager', pid):
            os.kill(pid, signal.SIGTERM)
        else:
            launch("blueman-manager", None, False, "blueman", _("Device Manager"))

    def on_adapters(self, menu_item):
        launch("blueman-adapters", None, False, "blueman", _("Adapter Preferences"))

    def on_local_services(self, menu_item):
        launch("blueman-services", None, False, "blueman", _("Service Preferences"))

    def on_about(self, menu_item):
        about = show_about_dialog("Blueman " + _("applet"), run=False)

        im = Gtk.Image(icon_name="blueman-plugins", pixel_size=16)
        button = Gtk.Button(label=_("Plugins"), visible=True, image=im)

        button.connect("clicked", self.on_plugins)

        about.action_area.pack_start(button, True, True, 0)
        about.action_area.reorder_child(button, 0)

        about.run()
        about.destroy()

    def on_plugins(self, button):
        def open_dialog():
            dialog = PluginDialog(self.Applet)
            dialog.run()
            dialog.destroy()
        GLib.idle_add(open_dialog)
