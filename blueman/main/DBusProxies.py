# coding=utf-8
from gi.repository import Gio, GLib
from gi.types import GObjectMeta


class DBusProxyFailed(Exception):
    pass


class ProxyBaseMeta(GObjectMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class ProxyBase(Gio.DBusProxy, metaclass=ProxyBaseMeta):
    def __init__(self, name, interface_name, object_path='/', systembus=False, *args, **kwargs):
        if systembus:
            bustype = Gio.BusType.SYSTEM
        else:
            bustype = Gio.BusType.SESSION

        super().__init__(
            g_name=name,
            g_interface_name=interface_name,
            g_object_path=object_path,
            g_bus_type=bustype,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs
        )

        try:
            self.init()
        except GLib.Error as e:
            raise DBusProxyFailed(e.message)


class Mechanism(ProxyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(name='org.blueman.Mechanism', interface_name='org.blueman.Mechanism',
                         object_path="/org/blueman/mechanism", systembus=True, *args, **kwargs)


class AppletService(ProxyBase):
    def __init__(self, *args, **kwargs):
        super().__init__(name='org.blueman.Applet', interface_name='org.blueman.Applet',
                         object_path="/org/blueman/applet", *args, **kwargs)
