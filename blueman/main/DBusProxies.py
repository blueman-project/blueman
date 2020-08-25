from gi.repository import Gio, GLib

from blueman.gobject import SingletonGObjectMeta


class DBusProxyFailed(Exception):
    pass


class ProxyBase(Gio.DBusProxy, metaclass=SingletonGObjectMeta):
    def __init__(self, name: str, interface_name: str, object_path: str = "/", systembus: bool = False,
                 flags: Gio.DBusProxyFlags = Gio.DBusProxyFlags.NONE) -> None:
        if systembus:
            bustype = Gio.BusType.SYSTEM
        else:
            bustype = Gio.BusType.SESSION

        super().__init__(
            g_name=name,
            g_interface_name=interface_name,
            g_object_path=object_path,
            g_bus_type=bustype,
            g_flags=flags
        )

        try:
            self.init()
        except GLib.Error as e:
            raise DBusProxyFailed(e.message)


class Mechanism(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name='org.blueman.Mechanism', interface_name='org.blueman.Mechanism',
                         object_path="/org/blueman/mechanism", systembus=True)


class AppletService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name='org.blueman.Applet', interface_name='org.blueman.Applet',
                         object_path="/org/blueman/Applet")


class ManagerService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name="org.blueman.Manager", interface_name="org.freedesktop.Application",
                         object_path="/org/blueman/Manager",
                         flags=Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION)

    def _call_action(self, name: str) -> None:
        def call_finish(proxy: "ManagerService", resp: Gio.AsyncResult) -> None:
            proxy.call_finish(resp)

        param = GLib.Variant('(sava{sv})', (name, [], {}))
        self.call('ActivateAction', param, Gio.DBusCallFlags.NONE, -1, None, call_finish)

    def startstop(self) -> None:
        if self.get_name_owner() is None:
            self._call_action("Activate")
        else:
            self._call_action("Quit")
