from importlib import import_module
import logging
import os
import sys
from blueman.main.DBusProxies import AppletService
from gi.repository import Gio, GLib


class BluemanTray(Gio.Application):
    def __init__(self) -> None:
        super().__init__(application_id="org.blueman.Tray", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self._active = False

    def do_activate(self) -> None:
        if self._active:
            logging.info("Already running, restarting instance")
            os.execv(sys.argv[0], sys.argv)

        Gio.bus_watch_name(Gio.BusType.SESSION, 'org.blueman.Applet', Gio.BusNameWatcherFlags.NONE,
                           self._on_name_appeared, self._on_name_vanished)
        self.hold()

    def _on_name_appeared(self, _connection: Gio.DBusConnection, name: str, _owner: str) -> None:
        logging.debug("Applet started on name %s, showing indicator" % name)

        applet = AppletService()
        indicator_name = applet.GetStatusIconImplementation()
        logging.info(f'Using indicator "{indicator_name}"')
        indicator_class = getattr(import_module('blueman.main.indicators.' + indicator_name), indicator_name)
        self.indicator = indicator_class(applet.GetIconName(), self._activate_menu_item, self._activate_status_icon)

        applet.connect('g-signal', self.on_signal)

        self.indicator.set_text(applet.GetText())
        self.indicator.set_visibility(applet.GetVisibility())
        self.indicator.set_menu(applet.GetMenu())

        self._active = True

    def _on_name_vanished(self, _connection: Gio.DBusConnection, _name: str) -> None:
        logging.debug("Applet shutdown or not available at startup")
        self.quit()

    def _activate_menu_item(self, *indexes: int) -> None:
        AppletService().ActivateMenuItem('(ai)', indexes)

    def _activate_status_icon(self) -> None:
        AppletService().Activate()

    def on_signal(self, _applet: AppletService, _sender_name: str, signal_name: str, args: GLib.Variant) -> None:
        if signal_name == 'IconNameChanged':
            self.indicator.set_icon(*args)
        elif signal_name == 'TextChanged':
            self.indicator.set_text(*args)
        elif signal_name == 'VisibilityChanged':
            self.indicator.set_visibility(*args)
        elif signal_name == 'MenuChanged':
            self.indicator.set_menu(*args)
