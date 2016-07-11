# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from gi.repository import Gio


class Mechanism(Gio.DBusProxy):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Mechanism, cls).__new__(cls)
            cls._instance._init(*args, **kwargs)
        return Mechanism._instance

    def __init__(self):
        pass

    def _init(self, *args, **kwargs):
        super(Mechanism, self).__init__(
            g_name='org.blueman.Mechanism',
            g_interface_name='org.blueman.Mechanism',
            g_object_path='/',
            g_bus_type=Gio.BusType.SYSTEM,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs)

        self.init()
