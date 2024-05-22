from gettext import gettext as _
import logging

from gi.repository import Gio, GLib

from blueman.gobject import SingletonGObjectMeta
from blueman.gui.Notification import Notification


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

    def activate(self) -> None:
        def call_finish(proxy: "ManagerService", resp: Gio.AsyncResult) -> None:
            try:
                proxy.call_finish(resp)
            except GLib.Error:
                # This can different errors, depending on the system configuration, typically:
                # * org.freedesktop.DBus.Error.Spawn.ChildExited if dbus-daemon tries to launch the service itself.
                # * org.freedesktop.DBus.Error.NoReply if the systemd integration is used.
                logging.error("Call to %s failed", self.get_name(), exc_info=True)
                Notification(
                    _("Failed to reach blueman-manager"),
                    _("It seems like blueman-manager could no get activated via D-Bus. "
                      "A typical cause for this is a broken graphical setup in the D-Bus activation environment "
                      "that can get resolved with a call to dbus-update-activation-environment, "
                      "typically issued from xinitrc (respectively the Sway config or similar)."),
                    0,
                ).show()

        param = GLib.Variant('(a{sv})', ({},))
        self.call("Activate", param, Gio.DBusCallFlags.NONE, -1, None, call_finish)

    def _call_action(self, name: str) -> None:
        def call_finish(proxy: "ManagerService", resp: Gio.AsyncResult) -> None:
            try:
                proxy.call_finish(resp)
            except GLib.Error:
                logging.error("Call to %s failed", self.get_name(), exc_info=True)

        param = GLib.Variant('(sava{sv})', (name, [], {}))
        self.call('ActivateAction', param, Gio.DBusCallFlags.NONE, -1, None, call_finish)

    def quit(self) -> None:
        self._call_action("Quit")
