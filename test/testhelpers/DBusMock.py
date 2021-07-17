from dbusmock import DBusTestCase
from gi.repository import Gio, GLib


class DBusMockObject:
    def __init__(self, name: str, path: str, system_bus: bool) -> None:
        self._proxy = Gio.DBusProxy(
            g_name=name,
            g_interface_name="org.freedesktop.DBus.Mock",
            g_object_path=path,
            g_connection=Gio.bus_get_sync(Gio.BusType.SYSTEM if system_bus else Gio.BusType.SESSION),
        )
        self._proxy.init()

    def add_method(self, interface: str, name: str, in_sig: str, out_sig: str, script: str) -> None:
        self._proxy.call_sync("AddMethod", GLib.Variant("(sssss)", (interface, name, in_sig, out_sig, script)),
                              Gio.DBusCallFlags.NONE, GLib.MAXINT)

    def add_property(self, interface: str, name: str, value: GLib.Variant) -> None:
        self._proxy.call_sync("AddProperty", GLib.Variant("(ssv)", (interface, name, value)),
                              Gio.DBusCallFlags.NONE, GLib.MAXINT)

    def set_property(self, interface: str, name: str, value: GLib.Variant) -> None:
        self._proxy.call_sync("org.freedesktop.DBus.Properties.Set", GLib.Variant("(ssv)", (interface, name, value)),
                              Gio.DBusCallFlags.NONE, GLib.MAXINT)


class DBusMock(DBusMockObject):
    def __init__(self, name: str, path: str, system_bus: bool) -> None:
        self._system_bus = system_bus
        self._process = DBusTestCase.spawn_server(name, path, "org.freedesktop.DBus.Mock", system_bus=system_bus)
        super().__init__(name, path, system_bus)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._process.terminate()
        self._process.wait()

    def add_object(self, path: str) -> DBusMockObject:
        self._proxy.call_sync(
            "AddObject", GLib.Variant("(ssa{sv}a(ssss))", (path, "org.freedesktop.DBus.Mock", {}, [])),
            Gio.DBusCallFlags.NONE, GLib.MAXINT)
        return DBusMockObject(self._proxy.props.g_name, path, self._system_bus)
