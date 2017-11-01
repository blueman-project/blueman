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

        applet.Plugins.Menu.add(self, 21)

        self.new_dev = self.Applet.Plugins.Menu.add(self, 30, text=_("_Set Up New Device") + "...",
                                                    icon_name="document-new", callback=self.on_setup_new)

        self.Applet.Plugins.Menu.add(self, 31)

        self.send = self.Applet.Plugins.Menu.add(self, 40, text=_("Send _Files to Device") + "...",
                                                 icon_name="blueman-send-file", callback=self.on_send)

        self.Applet.Plugins.Menu.add(self, 51)

        self.devices = self.Applet.Plugins.Menu.add(self, 60, text=_("_Devices") + "...", icon_name="blueman",
                                                    callback=self.on_devices)

        self.adapters = self.Applet.Plugins.Menu.add(self, 70, text=_("Adap_ters") + "...", icon_name="blueman-device",
                                                     callback=self.on_adapters)

        self.Applet.Plugins.Menu.add(self, 80, text=_("_Local Services") + "...", icon_name="preferences-desktop",
                                     callback=self.on_local_services)

        self.Applet.Plugins.Menu.add(self, 81)

        self.Applet.Plugins.Menu.add(self, 90, text="_Help", icon_name='help-about', callback=self.on_about)

        self.Applet.Plugins.Menu.add(self, 85, text=_("_Plugins"), icon_name="blueman-plugin", callback=self.on_plugins)

        self.Applet.Plugins.StatusIcon.connect("activate", lambda status_icon: self.on_devices(None))

    def change_sensitivity(self, sensitive):
        try:
            power = self.Applet.Plugins.PowerManager.GetBluetoothStatus()
        except:
            power = True

        sensitive = sensitive and self.Applet.Manager and power
        self.new_dev.set_sensitive(sensitive)
        self.send.set_sensitive(sensitive)
        self.devices.set_sensitive(sensitive)
        self.adapters.set_sensitive(sensitive)

    def on_manager_state_changed(self, state):
        self.change_sensitivity(state)

    def on_power_state_changed(self, manager, state):
        self.change_sensitivity(state)

    def on_setup_new(self):
        launch("blueman-assistant", None, False, "blueman", _("Bluetooth Assistant"))

    def on_send(self):
        launch("blueman-sendto", None, False, "blueman", _("File Sender"))

    def on_devices(self):
        lockfile = get_lockfile('blueman-manager')
        pid = get_pid(lockfile)
        if lockfile and pid and is_running('blueman-manager', pid):
            os.kill(pid, signal.SIGTERM)
        else:
            launch("blueman-manager", None, False, "blueman", _("Device Manager"))

    def on_adapters(self):
        launch("blueman-adapters", None, False, "blueman", _("Adapter Preferences"))

    def on_local_services(self):
        launch("blueman-services", None, False, "blueman", _("Service Preferences"))

    def on_about(self):
        about = show_about_dialog("Blueman " + _("applet"), run=False)

        im = Gtk.Image(icon_name="blueman-plugins", pixel_size=16)
        button = Gtk.Button(label=_("Plugins"), visible=True, image=im)

        button.connect("clicked", lambda _button: self.on_plugins())

        about.action_area.pack_start(button, True, True, 0)
        about.action_area.reorder_child(button, 0)

        about.run()
        about.destroy()

    def on_plugins(self):
        def open_dialog():
            dialog = PluginDialog(self.Applet)
            dialog.run()
            dialog.destroy()
        GLib.idle_add(open_dialog)
