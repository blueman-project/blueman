# coding=utf-8
from gi.repository import Gio

class AppletService(Gio.DBusProxy):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AppletService, cls).__new__(cls)
            cls._instance._init(*args, **kwargs)
        return AppletService._instance

    def __init__(self):
        pass

    def _init(self, *args, **kwargs):
        super(AppletService, self).__init__(
            g_name='org.blueman.Applet',
            g_interface_name='org.blueman.Applet',
            g_object_path='/',
            g_bus_type=Gio.BusType.SESSION,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs)

        self.init()
