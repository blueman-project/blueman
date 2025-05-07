from importlib import import_module
import logging
import os
import signal
import sys
from blueman.Functions import log_system_info
from blueman.main.DBusProxies import AppletMenuService
from gi.repository import Gio, GLib

from blueman.main.indicators.IndicatorInterface import IndicatorNotAvailable


class BluemanTray(Gio.Application):
    def __init__(self) -> None:
        super().__init__(application_id="org.blueman.Tray", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self._active = False

        def do_quit(_: object) -> bool:
            self.quit()
            return False

        log_system_info()

        s = GLib.unix_signal_source_new(signal.SIGINT)
        s.set_callback(do_quit)
        s.attach()

    def do_activate(self) -> None:
        if self._active:
            GLib.timeout_add_seconds(1, lambda: os.execv(sys.argv[0], sys.argv))
            logging.info("Already running, restarting instance")
            return

        Gio.bus_watch_name(Gio.BusType.SESSION, 'org.blueman.Applet', Gio.BusNameWatcherFlags.NONE,
                           self._on_name_appeared, self._on_name_vanished)
        self.hold()

    def _on_name_appeared(self, _connection: Gio.DBusConnection, name: str, _owner: str) -> None:
        logging.debug(f"Applet started on name {name}, showing indicator")

        menu_service = AppletMenuService()
        for indicator_name in menu_service.get_statusicon_implementations():
            indicator_class = getattr(import_module('blueman.main.indicators.' + indicator_name), indicator_name)
            try:
                self.indicator = indicator_class(self, menu_service.get_icon_name())
                break
            except IndicatorNotAvailable:
                logging.info(f'Indicator "{indicator_name}" is not available')
        logging.info(f'Using indicator "{self.indicator.__class__.__name__}"')

        menu_service.connect('g-signal', self.on_signal)

        self.indicator.set_tooltip_title(menu_service.get_tooltip_title())
        self.indicator.set_tooltip_text(menu_service.get_tooltip_text())
        self.indicator.set_visibility(menu_service.get_visibility())
        self.indicator.set_menu(menu_service.get_menu())

        self._active = True

    def _on_name_vanished(self, _connection: Gio.DBusConnection, _name: str) -> None:
        logging.debug("Applet shutdown or not available at startup")
        self.quit()

    def activate_menu_item(self, *indexes: int) -> None:
        AppletMenuService().ActivateMenuItem('(ai)', indexes)

    def activate_status_icon(self) -> None:
        AppletMenuService().Activate()

    def on_signal(self, _applet: AppletMenuService, _sender_name: str, signal_name: str, args: GLib.Variant) -> None:
        if signal_name == 'IconNameChanged':
            self.indicator.set_icon(*args)
        elif signal_name == 'ToolTipTitleChanged':
            self.indicator.set_tooltip_title(*args)
        elif signal_name == 'ToolTipTextChanged':
            self.indicator.set_tooltip_text(*args)
        elif signal_name == 'VisibilityChanged':
            self.indicator.set_visibility(*args)
        elif signal_name == 'MenuChanged':
            self.indicator.set_menu(*args)
