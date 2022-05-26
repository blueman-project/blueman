from gettext import gettext as _
from typing import Optional

from blueman.Functions import launch
from blueman.main.DBusProxies import ManagerService
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.gui.CommonUi import show_about_dialog
from blueman.gui.applet.PluginDialog import PluginDialog

import gi

from blueman.plugins.applet.PowerManager import PowerManager, PowerStateListener

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk


class StandardItems(AppletPlugin, PowerStateListener):
    __depends__ = ["StatusIcon", "Menu"]
    __unloadable__ = False
    __description__ = _("Adds standard menu items to the status icon menu")
    __author__ = "walmis"

    def on_load(self) -> None:
        self._plugin_window: Optional[Gtk.Window] = None

        self.parent.Plugins.Menu.add(self, 21)

        self.parent.Plugins.Menu.add(self, 31)

        self.send = self.parent.Plugins.Menu.add(self, 40, text=_("Send _Files to Device") + "…",
                                                 icon_name="blueman-send-symbolic", callback=self.on_send)

        self.parent.Plugins.Menu.add(self, 51)

        self.devices = self.parent.Plugins.Menu.add(self, 60, text=_("_Devices") + "…",
                                                    icon_name="bluetooth-symbolic",
                                                    callback=self.on_devices)

        self.adapters = self.parent.Plugins.Menu.add(self, 70, text=_("Adap_ters") + "…",
                                                     icon_name="bluetooth-symbolic",
                                                     callback=self.on_adapters)

        self.parent.Plugins.Menu.add(self, 80, text=_("_Local Services") + "…",
                                     icon_name="document-properties-symbolic",
                                     callback=self.on_local_services)

        self.parent.Plugins.Menu.add(self, 81)

        self.parent.Plugins.Menu.add(self, 90, text=_("_Help"), icon_name='help-about-symbolic',
                                     callback=self.on_about)

        self.parent.Plugins.Menu.add(self, 85, text=_("_Plugins"), icon_name="application-x-addon-symbolic",
                                     callback=self.on_plugins)

        self.parent.Plugins.StatusIcon.connect("activate", lambda _status_icon: self.on_devices())

    def change_sensitivity(self, sensitive: bool) -> None:
        if 'PowerManager' in self.parent.Plugins.get_loaded():
            power = self.parent.Plugins.PowerManager.get_bluetooth_status()
        else:
            power = True

        sensitive = sensitive and self.parent.Manager is not None and power
        self.send.set_sensitive(sensitive)
        self.devices.set_sensitive(sensitive)
        self.adapters.set_sensitive(sensitive)

    def on_manager_state_changed(self, state: bool) -> None:
        self.change_sensitivity(state)

    def on_power_state_changed(self, manager: PowerManager, state: bool) -> None:
        self.change_sensitivity(state)

    def on_send(self) -> None:
        launch("blueman-sendto", name=_("File Sender"))

    def on_devices(self) -> None:
        m = ManagerService()
        m.startstop()

    def on_adapters(self) -> None:
        launch("blueman-adapters", name=_("Adapter Preferences"))

    def on_local_services(self) -> None:
        launch("blueman-services", name=_("Service Preferences"))

    def on_about(self) -> None:
        about = show_about_dialog("Blueman " + _("applet"), run=False)

        im = Gtk.Image(icon_name="blueman-plugin", pixel_size=16)
        button = Gtk.Button(label=_("Plugins"), visible=True, image=im)

        button.connect("clicked", lambda _button: self.on_plugins())

        about.action_area.pack_start(button, True, True, 0)
        about.action_area.reorder_child(button, 0)

        about.run()
        about.destroy()

    def on_plugins(self) -> None:
        def on_close(win: Gtk.Window, _event: Gdk.Event) -> bool:
            win.destroy()
            self._plugin_window = None
            return False

        if self._plugin_window:
            self._plugin_window.present()
        else:
            self._plugin_window = PluginDialog(self.parent)
            self._plugin_window.connect("delete-event", on_close)
            self._plugin_window.show()
