import logging
from gettext import gettext as _
from typing import Optional

from blueman.bluez.Manager import Manager
from blueman.bluez.errors import DBusNoSuchAdapterError
from blueman.Functions import *
from blueman.Constants import UI_PATH
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList
from blueman.gui.manager.ManagerToolbar import ManagerToolbar
from blueman.gui.manager.ManagerMenu import ManagerMenu
from blueman.gui.manager.ManagerStats import ManagerStats
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.Config import Config
from blueman.main.DBusProxies import AppletService, DBusProxyFailed
from blueman.gui.CommonUi import ErrorDialog
from blueman.gui.MessageArea import MessageArea
from blueman.gui.Notification import Notification
from blueman.main.PluginManager import PluginManager
import blueman.plugins.manager
from blueman.plugins.ManagerPlugin import ManagerPlugin

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio


class Blueman(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="org.blueman.Manager")

    window: Optional[Gtk.ApplicationWindow]

    def do_startup(self):
        def doquit(_a, _param):
            self.quit()

        Gtk.Application.do_startup(self)
        self.window = None

        self.Config = Config("org.blueman.general")

        quit_action = Gio.SimpleAction.new("Quit", None)
        quit_action.connect("activate", doquit)
        self.add_action(quit_action)

    def do_activate(self):
        if not self.window:
            self.window = Gtk.ApplicationWindow(application=self, name="BluemanManager", icon_name="blueman",
                                                title="Bluetooth Devices")
            w, h, x, y = self.Config["window-properties"]
            if w and h:
                self.window.resize(w, h)
            if x and y:
                self.window.move(x, y)

            # Connect to configure event to store new window position and size
            self.window.connect("configure-event", self._on_configure)

            self.Builder = Gtk.Builder()
            self.Builder.set_translation_domain("blueman")
            self.Builder.add_from_file(UI_PATH + "/manager-main.ui")

            grid = self.Builder.get_object("grid")
            self.window.add(grid)

            toolbar = self.Builder.get_object("toolbar")
            statusbar = self.Builder.get_object("statusbar")

            self.Plugins = PluginManager(ManagerPlugin, blueman.plugins.manager, self)
            self.Plugins.load_plugin()

            area = MessageArea()
            grid.attach(area, 0, 3, 1, 1)

            self._applethandlerid: Optional[int] = None

            # Add margin for resize grip or it will overlap
            if self.window.get_has_resize_grip():
                margin_right = statusbar.get_margin_right()
                statusbar.set_margin_right(margin_right + 10)

            def bt_status_changed(status):
                assert self.window is not None
                if not status:
                    self.window.hide()
                    check_bluetooth_status(_("Bluetooth needs to be turned on for the device manager to function"),
                                           self.quit)
                else:
                    self.window.show()

            def on_applet_signal(_proxy, _sender, signal_name, params):
                if signal_name == 'BluetoothStatusChanged':
                    status = params.unpack()
                    bt_status_changed(status)

            def on_dbus_name_vanished(_connection, name):
                logging.info(name)
                if self._applethandlerid:
                    self.Applet.disconnect(self._applethandlerid)
                    self._applethandlerid = None

                self.hide()

                d = ErrorDialog(
                    _("Connection to BlueZ failed"),
                    _("Bluez daemon is not running, blueman-manager cannot continue.\n"
                      "This probably means that there were no Bluetooth adapters detected "
                      "or Bluetooth daemon was not started."),
                    icon_name="blueman")
                d.run()
                d.destroy()

                # FIXME ui can handle BlueZ start/stop but we should inform user
                self.quit()

            def on_dbus_name_appeared(_connection, name, owner):
                logging.info(f"{name} {owner}")
                setup_icon_path()

                try:
                    self.Applet = AppletService()
                except DBusProxyFailed:
                    print("Blueman applet needs to be running")
                    bmexit()

                check_bluetooth_status(_("Bluetooth needs to be turned on for the device manager to function"),
                                       lambda: Gtk.main_quit())

                manager = Manager()
                try:
                    manager.get_adapter(self.Config['last-adapter'])
                except DBusNoSuchAdapterError:
                    logging.error('Default adapter not found, trying first available.')
                    try:
                        manager.get_adapter(None)
                    except DBusNoSuchAdapterError:
                        logging.error('No adapter(s) found, exiting')
                        bmexit()

                self._applethandlerid = self.Applet.connect('g-signal', on_applet_signal)

                sw = self.Builder.get_object("scrollview")
                # Disable overlay scrolling
                if Gtk.get_minor_version() >= 16:
                    sw.props.overlay_scrolling = False

                self.List = ManagerDeviceList(adapter=self.Config["last-adapter"], inst=self)

                self.List.show()
                sw.add(self.List)

                self.Toolbar = ManagerToolbar(self)
                self.Menu = ManagerMenu(self)
                self.Stats = ManagerStats(self)

                if self.List.is_valid_adapter():
                    self.List.display_known_devices(autoselect=True)

                self.List.connect("adapter-changed", self.on_adapter_changed)

                self.Config.bind_to_widget("show-toolbar", toolbar, "visible")
                self.Config.bind_to_widget("show-statusbar", statusbar, "visible")

            Manager.watch_name_owner(on_dbus_name_appeared, on_dbus_name_vanished)

        self.window.present_with_time(Gtk.get_current_event_time())

    def _on_configure(self, window, event):
        width, height, x, y = self.Config["window-properties"]
        if event.x != x or event.y != y or event.width != width or event.height != height:
            self.Config["window-properties"] = [event.width, event.height, event.x, event.y]
        return False

    def on_adapter_changed(self, lst, adapter):
        if adapter is not None:
            self.List.display_known_devices(autoselect=True)

    def inquiry(self):
        def prop_changed(lst, adapter, key_value):
            key, value = key_value
            if key == "Discovering" and not value:
                prog.finalize()

                self.List.disconnect(s1)
                self.List.disconnect(s2)

        def on_progress(lst, frac):
            if abs(1.0 - frac) <= 0.00001:
                if not prog.started():
                    prog.start()
            else:
                prog.fraction(frac)

        prog = ManagerProgressbar(self, text=_("Searching"))
        prog.connect("cancelled", lambda x: self.List.stop_discovery())
        try:
            self.List.discover_devices()
        except Exception as e:
            prog.finalize()
            MessageArea.show_message(*e_(e))

        s1 = self.List.connect("discovery-progress", on_progress)
        s2 = self.List.connect("adapter-property-changed", prop_changed)

    @staticmethod
    def setup(device):
        command = f"blueman-assistant --device={device['Address']}"
        launch(command, name=_("Bluetooth Assistant"))

    @staticmethod
    def bond(device):
        def error_handler(e):
            logging.exception(e)
            message = f"Pairing failed for:\n{device['Alias']} ({device['Address']})"
            Notification('Bluetooth', message, icon_name="blueman").show()

        device.pair(error_handler=error_handler)

    @staticmethod
    def adapter_properties():
        launch("blueman-adapters", name=_("Adapter Preferences"))

    @staticmethod
    def toggle_trust(device):
        device['Trusted'] = not device['Trusted']

    def send(self, device, f=None):
        adapter = self.List.Adapter

        assert adapter

        command = f"blueman-sendto --source={adapter['Address']} --device={device['Address']}"
        launch(command, name=_("File Sender"))

    def remove(self, device):
        assert self.List.Adapter
        self.List.Adapter.remove_device(device)
