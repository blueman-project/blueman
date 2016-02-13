# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)


class AppletService(dbus.proxies.Interface):
    __inst__ = None

    def __new__(cls):
        if not AppletService.__inst__:
            AppletService.__inst__ = object.__new__(cls)

        return AppletService.__inst__

    def __init__(self):
        self.bus = dbus.SessionBus()

        service = self.bus.get_object("org.blueman.Applet", "/", follow_name_owner_changes=True)
        super(AppletService, self).__init__(service, "org.blueman.Applet")
