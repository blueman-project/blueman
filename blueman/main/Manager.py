# coding=utf-8
import logging
from locale import bind_textdomain_codeset

import blueman.bluez as bluez
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
from gi.repository import Gtk


class Blueman(Gtk.Window):
    def __init__(self):
        super().__init__(title=_("Bluetooth Devices"))

        self._applet_sig = None

        self.Config = Config("org.blueman.general")

        self.Builder = Gtk.Builder()
        self.Builder.set_translation_domain("blueman")
        bind_textdomain_codeset("blueman", "UTF-8")
        self.Builder.add_from_file(UI_PATH + "/manager-main.ui")

        grid = self.Builder.get_object("grid")
        self.add(grid)
        self.set_name("BluemanManager")

        self.Plugins = PluginManager(ManagerPlugin, blueman.plugins.manager, self)
        self.Plugins.load_plugin()

        area = MessageArea()
        grid.attach(area, 0, 3, 1, 1)

        # Add margin for resize grip or it will overlap
        if self.get_has_resize_grip():
            statusbar = self.Builder.get_object("statusbar")
            margin_right = statusbar.get_margin_right()
            statusbar.set_margin_right(margin_right + 10)

        def do_present(time):
            if self.props.visible:
                self.present_with_time(time)

        check_single_instance("blueman-manager", do_present)

        def on_window_delete(window, event):
            w, h = self.get_size()
            x, y = self.get_position()
            self.Config["window-properties"] = [w, h, x, y]
            Gtk.main_quit()

        def bt_status_changed(status):
            if not status:
                self.hide()
                check_bluetooth_status(_("Bluetooth needs to be turned on for the device manager to function"),
                                       lambda: Gtk.main_quit())
            else:
                self.show()

        def on_applet_signal(_proxy, _sender, signal_name, params):
            if signal_name == 'BluetoothStatusChanged':
                status = params.unpack()
                bt_status_changed(status)

        def on_dbus_name_vanished(_connection, name):
            logging.info(name)
            if self._applet_sig is not None:
                self.Applet.disconnect(self._applet_sig)
                self._applet_sig = None

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
            Gtk.main_quit()

        def on_dbus_name_appeared(_connection, name, owner):
            logging.info("%s %s" % (name, owner))
            setup_icon_path()

            try:
                self.Applet = AppletService()
            except DBusProxyFailed:
                print("Blueman applet needs to be running")
                exit()

            check_bluetooth_status(_("Bluetooth needs to be turned on for the device manager to function"),
                                   lambda: Gtk.main_quit())

            manager = bluez.Manager()
            try:
                manager.get_adapter(self.Config['last-adapter'])
            except bluez.errors.DBusNoSuchAdapterError:
                logging.error('Default adapter not found, trying first available.')
                try:
                    manager.get_adapter(None)
                except bluez.errors.DBusNoSuchAdapterError:
                    logging.error('No adapter(s) found, exiting')
                    exit(1)

            self._applet_sig = self.Applet.connect('g-signal', on_applet_signal)

            self.connect("delete-event", on_window_delete)
            self.props.icon_name = "blueman"

            w, h, x, y = self.Config["window-properties"]
            if w and h:
                self.resize(w, h)
            if x and y:
                self.move(x, y)

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

            toolbar = self.Builder.get_object("toolbar")
            statusbar = self.Builder.get_object("statusbar")

            self.Config.bind_to_widget("show-toolbar", toolbar, "visible")
            self.Config.bind_to_widget("show-statusbar", statusbar, "visible")

            self.show()

        bluez.Manager.watch_name_owner(on_dbus_name_appeared, on_dbus_name_vanished)

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

    def setup(self, device):
        command = "blueman-assistant --device=%s" % device['Address']
        launch(command, None, False, "blueman", _("Bluetooth Assistant"))

    def bond(self, device):
        def error_handler(e):
            logging.exception(e)
            message = 'Pairing failed for:\n%s (%s)' % (device['Alias'], device['Address'])
            Notification('Bluetooth', message, icon_name="blueman").show()

        device.pair(error_handler=error_handler)

    def adapter_properties(self):
        launch("blueman-adapters", None, False, "blueman", _("Adapter Preferences"))

    def toggle_trust(self, device):
        device['Trusted'] = not device['Trusted']

    def send(self, device, f=None):
        adapter = self.List.Adapter

        command = "blueman-sendto --source=%s --device=%s" % (adapter["Address"], device['Address'])
        launch(command, None, False, "blueman", _("File Sender"))

    def remove(self, device):
        self.List.Adapter.remove_device(device)
