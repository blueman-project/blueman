# coding=utf-8
import logging
from importlib import import_module
from blueman.main.AppletService import AppletService
from gi.repository import Gio


class BluemanTray(Gio.Application):
    def __init__(self):
        super().__init__(application_id="org.blueman.Tray", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.applet = None
        self.indicator = None

    def do_startup(self):
        Gio.Application.do_startup(self)

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit)
        self.add_action(quit_action)

    def do_activate(self):
        if self.indicator:
            logging.info("Already an instance running")
            return

        Gio.bus_watch_name(Gio.BusType.SESSION, 'org.blueman.Applet',
                           Gio.BusNameWatcherFlags.NONE, self._on_name_appeared, self._on_name_vanished)

        self.hold()

    def _on_quit(self, *args):
        logging.info("Shutting down")
        self.release()

    def _on_name_appeared(self, connection, name, owner):
        logging.debug("%s appeared, showing indicator" % name)

        self.applet = AppletService()
        self.applet.connect('g-signal', self.on_signal)

        indicator_name = self.applet.GetStatusIconImplementation()
        logging.info('Using indicator "%s"' % indicator_name)
        indicator_class = getattr(import_module('blueman.main.indicators.' + indicator_name), indicator_name)
        self.indicator = indicator_class(self.applet.GetIconName(), self._activate_menu_item, self._activate_status_icon)

        self.indicator.set_text(self.applet.GetText())
        self.indicator.set_visibility(self.applet.GetVisibility())
        self.indicator.set_menu(self.applet.GetMenu())

    def _on_name_vanished(self, connection, name):
        logging.debug("%s vanished, stopping tray" % name)
        self._on_quit()

    def _activate_menu_item(self, *indexes):
        return self.applet.ActivateMenuItem('(ai)', indexes)

    def _activate_status_icon(self):
        return self.applet.Activate()

    def on_signal(self, _applet, sender_name, signal_name, args):
        if signal_name == 'IconNameChanged':
            self.indicator.set_icon(*args)
        elif signal_name == 'TextChanged':
            self.indicator.set_text(*args)
        elif signal_name == 'VisibilityChanged':
            self.indicator.set_visibility(*args)
        elif signal_name == 'MenuChanged':
            self.indicator.set_menu(*args)
