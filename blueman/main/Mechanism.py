# coding=utf-8
from gi.repository import Gio
from gi.types import GObjectMeta


class MechanismMeta(GObjectMeta):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Mechanism(Gio.DBusProxy, metaclass=MechanismMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(
            g_name='org.blueman.Mechanism',
            g_interface_name='org.blueman.Mechanism',
            g_object_path='/',
            g_bus_type=Gio.BusType.SYSTEM,
            g_flags=Gio.DBusProxyFlags.NONE,
            *args, **kwargs)

        self.init()
