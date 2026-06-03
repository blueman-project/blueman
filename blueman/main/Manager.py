import logging
import signal
from gettext import gettext as _
from typing import Any
from collections.abc import Callable

from blueman.bluez.Adapter import Adapter
from blueman.bluez.Device import Device
from blueman.bluez.Manager import Manager
from blueman.Constants import WEBSITE
from blueman.Functions import *
from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList
from blueman.gui.manager.ManagerToolbar import ManagerToolbar
from blueman.gui.manager.ManagerMenu import ManagerMenu
from blueman.gui.manager.ManagerStats import ManagerStats
from blueman.gui.manager.ManagerProgressbar import ManagerProgressbar
from blueman.main.Builder import Builder
from blueman.gui.CommonUi import ErrorDialog, show_about_dialog
from blueman.main.DBusProxies import (
    AppletService,
    AppletPowerManagerService,
    DBusProxyFailed,
    DBus,
    AppletServiceApplication
)
from blueman.gui.Notification import Notification
from blueman.main.PluginManager import PluginManager
import blueman.plugins.manager
from blueman.plugins.ManagerPlugin import ManagerPlugin

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gio, Gdk, GLib


class Blueman(Gtk.Application):
    window: Gtk.ApplicationWindow | None

    def __init__(self) -> None:
        super().__init__(application_id="org.blueman.Manager")
        self._applet_was_running = DBus().NameHasOwner("(s)", AppletService.NAME)

        def do_quit(_: object) -> bool:
            self.quit()
            return False

        log_system_info()

        s = GLib.unix_signal_source_new(signal.SIGINT)
        s.set_callback(do_quit)
        s.attach()

        setup_icon_path()

        try:
            self.Applet = AppletService()
            self.Applet.connect('g-signal', self.on_applet_signal)
            self.PowerManager = AppletPowerManagerService()
            self.PowerManager.connect('g-signal', self.on_applet_signal)
        except DBusProxyFailed:
            print("Blueman applet needs to be running")
            bmexit()

        self.Plugins = PluginManager(ManagerPlugin, blueman.plugins.manager, self)
        self.Plugins.load_plugin()

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        self.window = None

        self.Config = Gio.Settings(schema_id="org.blueman.general")

        self.builder = Builder("manager-main.ui")

        self._infobar = self.builder.get_widget("message_area", Gtk.InfoBar)
        self._infobar.connect("response", self._infobar_response)
        self._infobar_bt: str = ""

        self.register_action("inquiry", self.simple_action)
        self.register_action("bond", self.simple_action)
        self.register_action("trust-toggle", self.simple_action)
        self.register_action("remove", self.simple_action)
        self.register_action("send", self.simple_action)
        self.register_action("report", self.simple_action)
        self.register_action("about", self.simple_action)
        self.register_action("plugins", self.simple_action)
        self.register_action("services", self.simple_action)
        self.register_action("preferences", self.simple_action)

        self.register_action("Quit", self.simple_action)
        self.set_accels_for_action("app.Quit", ["<Ctrl>q", "<Ctrl>w"])

        self.register_settings_action("sort-descending")
        self.register_settings_action("show-toolbar")
        self.register_settings_action("show-statusbar")
        self.register_settings_action("hide-unnamed")
        self.register_settings_action("sort-by")

        bt_status_action = Gio.SimpleAction.new_stateful("bluetooth_status", None, GLib.Variant.new_boolean(False))
        bt_status_action.connect("change-state", self._on_bt_state_changed)
        self.add_action(bt_status_action)

        Manager.watch_name_owner(self.on_dbus_name_appeared, self.on_dbus_name_vanished)

    def do_shutdown(self) -> None:
        Gtk.Application.do_shutdown(self)

        if not self._applet_was_running:
            AppletServiceApplication().stop()

    def do_activate(self) -> None:
        if not self.window:
            self.window = self.builder.get_widget("manager_window", Gtk.ApplicationWindow)
            self.window.set_application(self)
            w, h, x, y = self.Config["window-properties"]
            if w and h:
                self.window.resize(w, h)
            if x and y:
                self.window.move(x, y)

            # Connect to configure event to store new window position and size
            self.window.connect("configure-event", self._on_configure)

        self.window.present_with_time(Gtk.get_current_event_time())

    def on_applet_signal(self, _proxy: AppletService | AppletPowerManagerService, _sender: str, signal_name: str,
                         params: GLib.Variant) -> None:
        action = self.lookup_action("bluetooth_status")

        if signal_name == 'BluetoothStatusChanged':
            status = params.unpack()[0]
            action.change_state(GLib.Variant.new_boolean(status))
        elif signal_name == "PluginsChanged":
            if "PowerManager" in self.Applet.QueryPlugins():
                status = self.PowerManager.get_bluetooth_status()
                action.change_state(GLib.Variant.new_boolean(status))

            self.Toolbar._update_buttons(self.List.Adapter)

    def on_dbus_name_appeared(self, _connection: Gio.DBusConnection, name: str, owner: str) -> None:
        logging.info(f"{name} {owner}")

        sw = self.builder.get_widget("scrollview", Gtk.ScrolledWindow)
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
            self.List.populate_devices()

        self.List.connect("adapter-changed", self.on_adapter_changed)

        pm_available = "PowerManager" in self.Applet.QueryPlugins()
        action_status = self.PowerManager.get_bluetooth_status() if pm_available else False
        bt_status_action = self.lookup_action("bluetooth_status")
        bt_status_action.change_state(GLib.Variant.new_boolean(action_status))

    def on_dbus_name_vanished(self, _connection: Gio.DBusConnection, name: str) -> None:
        logging.info(name)

        if self.window is not None:
            self.window.hide()

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

    def _on_bt_state_changed(self, action: Gio.SimpleAction, state_variant: GLib.Variant) -> None:
        action.set_state(state_variant)

        state = state_variant.unpack()
        self.PowerManager.set_bluetooth_status(state)

        if state:
            icon_name = "bluetooth"
            tooltip_text = _("Click to disable.")
        else:
            icon_name = "bluetooth-disabled"
            tooltip_text = _("Click to enable.")

        box = self.builder.get_widget("bt_status_box", Gtk.Box)
        image = self.builder.get_widget("im_bluetooth_status", Gtk.Image)
        box.set_tooltip_text(tooltip_text)
        image.props.icon_name = icon_name

    def _on_configure(self, _window: Gtk.ApplicationWindow, event: Gdk.EventConfigure) -> bool:
        width, height, x, y = self.Config["window-properties"]
        if event.x != x or event.y != y or event.width != width or event.height != height:
            self.Config["window-properties"] = [event.width, event.height, event.x, event.y]
        return False

    def register_settings_action(self, name: str) -> None:
        action = self.Config.create_action(name)
        self.add_action(action)

    def register_action(self, name: str, callback: Callable[[Gio.SimpleAction, Any | None], None],
                        vtype: GLib.VariantType | None = None) -> None:
        if name in self.list_actions():
            logging.error(f"{name} already exists")
        else:
            action = Gio.SimpleAction.new(name, vtype)
            action.connect("activate", callback)
            self.add_action(action)

    def simple_action(self, action: Gio.SimpleAction, param: GLib.Variant | None) -> None:
        match action.get_name():
            case "Quit":
                self.quit()
            case "inquiry":
                self.inquiry()
            case "bond":
                device = self.List.get_selected_device()
                if device is not None:
                    self.bond(device)
            case "trust-toggle":
                device = self.List.get_selected_device()
                if device is not None:
                    self.toggle_trust(device)
            case "remove":
                device = self.List.get_selected_device()
                if device is not None:
                    self.remove(device)
            case "send":
                device = self.List.get_selected_device()
                if device is not None:
                    self.send(device)
            case "report":
                launch(f"xdg-open {WEBSITE}/issues", system=True)
            case "about":
                widget = self.window.get_toplevel() if self.window else None
                assert isinstance(widget, Gtk.Window)
                show_about_dialog('Blueman ' + _('Device Manager'), parent=widget)
            case "plugins":
                self.Applet.OpenPluginDialog()
            case "services":
                launch("blueman-services", name=_("Service Preferences"))
            case "preferences":
                self.adapter_properties()
            case _ as name:
                logging.error(f"Unknown action: {name}")

    def on_adapter_changed(self, lst: ManagerDeviceList, adapter: str) -> None:
        if adapter is not None:
            self.List.populate_devices()

    def inquiry(self) -> None:
        def prop_changed(_lst: ManagerDeviceList, _adapter: Adapter, key_value: tuple[str, Any]) -> None:
            key, value = key_value
            if key == "Discovering" and not value:
                prog.finalize()

                self.List.disconnect(s1)
                self.List.disconnect(s2)

        def on_progress(_lst: ManagerDeviceList, frac: float) -> None:
            if abs(1.0 - frac) <= 0.00001:
                if not prog.started():
                    prog.start()
            else:
                prog.fraction(frac)

        prog = ManagerProgressbar(self, text=_("Searching"))
        prog.connect("cancelled", lambda x: self.List.stop_discovery())

        def on_error(e: Exception) -> None:
            prog.finalize()
            self.infobar_update(*e_(e))

        self.List.discover_devices(error_handler=on_error)

        s1 = self.List.connect("discovery-progress", on_progress)
        s2 = self.List.connect("adapter-property-changed", prop_changed)

    def infobar_update(self, message: str, bt: str | None = None, info: str | None = None) -> None:
        backtace_button = self.builder.get_widget("ib_backtrace_button", Gtk.Button)
        msg_lbl = self.builder.get_widget("ib_message", Gtk.Label)
        info_image = self.builder.get_widget("ib_info_image", Gtk.Image)

        info_image.set_visible(False if info is None else True)
        info_image.set_tooltip_text("" if info is None else info)

        if bt is not None:
            msg_lbl.set_text(f"{message}…")
            self._infobar_bt = f"{message}\n{bt}"
            backtace_button.show()
            self._infobar.set_message_type(Gtk.MessageType.ERROR)
        else:
            backtace_button.hide()
            msg_lbl.set_text(f"{message}")
            self._infobar.set_message_type(Gtk.MessageType.INFO)

        self._infobar.set_visible(True)
        self._infobar.set_revealed(True)

    def _infobar_response(self, info_bar: Gtk.InfoBar, response_id: int) -> None:
        def hide() -> bool:
            self._infobar.set_visible(False)
            return False

        logging.debug(f"Response: {response_id}")
        if response_id == Gtk.ResponseType.CLOSE:
            self._infobar_bt = ""
            info_bar.set_revealed(False)
            GLib.timeout_add(250, hide)  # transition is 250.
        elif response_id == 0:
            dialog = Gtk.MessageDialog(parent=self.window, type=Gtk.MessageType.INFO, modal=True,
                                       buttons=Gtk.ButtonsType.CLOSE, text=self._infobar_bt)
            dialog.connect("response", lambda d, _i: d.destroy())
            dialog.connect("close", lambda d: d.destroy())
            dialog.show()

    @staticmethod
    def bond(device: Device) -> None:
        def error_handler(e: Exception) -> None:
            logging.exception(e)
            message = f"Pairing failed for:\n{device.display_name} ({device['Address']})"
            Notification('Bluetooth', message, icon_name="blueman").show()

        device.pair(error_handler=error_handler)

    @staticmethod
    def adapter_properties() -> None:
        launch("blueman-adapters", name=_("Adapter Preferences"))

    @staticmethod
    def toggle_trust(device: Device) -> None:
        device['Trusted'] = not device['Trusted']

    @staticmethod
    def toggle_blocked(device: Device) -> None:
        device['Blocked'] = not device['Blocked']

    def send(self, device: Device) -> None:
        adapter = self.List.Adapter

        assert adapter

        command = f"blueman-sendto --source={adapter['Address']} --device={device['Address']}"
        launch(command, name=_("File Sender"))

    def remove(self, device: Device) -> None:
        assert self.List.Adapter
        self.List.Adapter.remove_device(device)
