from gi.repository import Gio, GLib

from blueman.gobject import SingletonGObjectMeta


class DBusProxyFailed(Exception):
    pass


class ProxyBase(Gio.DBusProxy, metaclass=SingletonGObjectMeta):
    def __init__(self, name, interface_name, object_path='/', systembus=False, flags=0, *args, **kwargs):
        if systembus:
            bustype = Gio.BusType.SYSTEM
        else:
            bustype = Gio.BusType.SESSION

        super().__init__(
            g_name=name,
            g_interface_name=interface_name,
            g_object_path=object_path,
            g_bus_type=bustype,
            g_flags=flags,
            *args, **kwargs
        )

        try:
            self.init()
        except GLib.Error as e:
            raise DBusProxyFailed(e.message)


class Mechanism(ProxyBase):
    def __init__(self):
        super().__init__(name='org.blueman.Mechanism', interface_name='org.blueman.Mechanism',
                         object_path="/org/blueman/mechanism", systembus=True)


class AppletService(ProxyBase):
    def __init__(self):
        super().__init__(name='org.blueman.Applet', interface_name='org.blueman.Applet',
                         object_path="/org/blueman/Applet")
