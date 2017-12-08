from importlib import import_module
import logging
import os
import sys

from blueman.main.DBusProxies import AppletService

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import (Gio, GLib)


class BluemanTray(Gio.Application):
    def __init__(self):
        super().__init__(application_id="org.blueman.Tray", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self._active = False
        self.indicator = None

    def do_startup(self):
        Gio.Application.do_startup(self)

        restart_action = Gio.SimpleAction.new("Restart", None)
        restart_action.connect("activate", self._on_restart)
        self.add_action(restart_action)

    def do_activate(self):
        if self._active:
            print("Already an instance running")
            return

        Gio.bus_watch_name(Gio.BusType.SESSION, 'org.blueman.Applet',
                           Gio.BusNameWatcherFlags.NONE, self._on_name_appeared, self._on_name_vanished)

        self.hold()

    def _on_restart(self, _action, _param):
        def restart():
            os.execv(sys.argv[0], sys.argv)
        logging.info("Restarting tray")

        # Allow the dbus method to return
        GLib.timeout_add_seconds(1, restart)

    def _on_name_appeared(self, connection, name, owner):
        logging.debug("Applet started on name %s, showing indicator" % name)

        applet = AppletService()
        indicator_name = applet.GetStatusIconImplementation()
        logging.info('Using indicator "%s"' % indicator_name)
        indicator_class = getattr(import_module('blueman.main.indicators.' + indicator_name), indicator_name)
        self.indicator = indicator_class(applet.GetIconName(), self._activate_menu_item, self._activate_status_icon)

        applet.connect('g-signal', self.on_signal)

        self.indicator.set_text(applet.GetText())
        self.indicator.set_visibility(applet.GetVisibility())
        self.indicator.set_menu(applet.GetMenu())

        self._active = True

    def _on_name_vanished(self, connection, name):
        logging.debug("Applet on name %s shutdown, hiding indicator" % name)
        self.indicator.set_visibility(False)
        self.quit()

    def _activate_menu_item(self, *indexes):
        return AppletService().ActivateMenuItem('(ai)', indexes)

    def _activate_status_icon(self):
        return AppletService().Activate()

    def on_signal(self, _applet, sender_name, signal_name, args):
        if signal_name == 'IconNameChanged':
            self.indicator.set_icon(*args)
        elif signal_name == 'TextChanged':
            self.indicator.set_text(*args)
        elif signal_name == 'VisibilityChanged':
            self.indicator.set_visibility(*args)
        elif signal_name == 'MenuChanged':
            self.indicator.set_menu(*args)
