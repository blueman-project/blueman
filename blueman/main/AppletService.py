# coding=utf-8
from gi.repository import Gio
from gi.types import GObjectMeta


class AppletServiceMeta(GObjectMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class AppletService(Gio.DBusProxy, metaclass=AppletServiceMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(
            g_name='org.blueman.Applet',
            g_interface_name='org.blueman.Applet',
            g_object_path='/',
            g_bus_type=Gio.BusType.SESSION,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs)

        self.init()
