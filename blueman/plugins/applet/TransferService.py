from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.Transfer import Transfer

from gi.repository import GObject
from gi.repository import Gtk
import dbus
import dbus.service


class TransferService(AppletPlugin):
    __author__ = "Walmis"
    __description__ = _("Provides OBEX file transfer capabilities")
    __icon__ = "blueman-send-file"

    def on_load(self, applet):
        self.Transfer = None

        self.sess_bus = dbus.SessionBus()

        self.__watch = dbus.bus.NameOwnerWatch(self.sess_bus, "org.openobex", self.on_obex_owner_changed)

    # self.try_start_ods()

    def on_unload(self):
        if self.__watch:
            self.__watch.cancel()

        if self.Transfer:
            self.Transfer.DisconnectAll()

        self.Transfer = None

    def on_manager_state_changed(self, state):

        if state:
            self.try_start_ods()

        else:
            if self.Transfer:
                self.Transfer.DisconnectAll()
                self.Transfer = None

    def try_start_ods(self):
        try:
            self.sess_bus.start_service_by_name("org.openobex")
        except dbus.DBusException as e:
            dprint("Could not acquire obex-data-server", e)

    def on_obex_owner_changed(self, owner):
        dprint("obex owner changed:", owner)
        if owner != "":
            self.Transfer = Transfer(self.Applet)

        else:
            if self.Transfer:
                self.Transfer.DisconnectAll()
            self.Transfer = None

    @dbus.service.method('org.blueman.Applet', in_signature="ss", out_signature="")
    def TransferControl(self, pattern, action):
        dprint(pattern, action)
        if not self.Transfer:
            return

        if action == "destroy":
            self.Transfer.destroy_server(pattern)
        elif action == "stop":
            server = self.Transfer.get_server(pattern)
            if server != None:
                server.Stop()

        elif action == "create":
            self.Transfer.create_server(pattern)

        elif action == "start":
            self.Transfer.start_server(pattern)

        else:
            dprint("Got unknown action")

    @dbus.service.method('org.blueman.Applet', in_signature="s", out_signature="i")
    def TransferStatus(self, pattern):
        if not self.Transfer:
            return -1
        server = self.Transfer.get_server(pattern)
        if server != None:
            if server.IsStarted():
                return 2
            else:
                return 1
        else:
            return 0
