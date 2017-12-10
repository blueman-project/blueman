from importlib import import_module
import logging

from blueman.Functions import check_single_instance
from blueman.main.DBusProxies import AppletService

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio


class BluemanTray(object):
    def __init__(self):
        check_single_instance("blueman-tray")

        applet = AppletService()

        main_loop = GLib.MainLoop()

        Gio.bus_watch_name(Gio.BusType.SESSION, 'org.blueman.Applet',
                           Gio.BusNameWatcherFlags.NONE, None, lambda _connection, _name: main_loop.quit())

        indicator_name = applet.GetStatusIconImplementation()
        logging.info('Using indicator "%s"' % indicator_name)
        indicator_class = getattr(import_module('blueman.main.indicators.' + indicator_name), indicator_name)
        self.indicator = indicator_class(applet.GetIconName(), self._activate_menu_item, self._activate_status_icon)

        applet.connect('g-signal', self.on_signal)

        self.indicator.set_text(applet.GetText())
        self.indicator.set_visibility(applet.GetVisibility())
        self.indicator.set_menu(applet.GetMenu())

        main_loop.run()

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
