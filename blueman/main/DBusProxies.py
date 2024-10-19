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

    def call_method(self, name: str, params: GLib.Variant) -> None:
        def call_finish(proxy: ProxyBase, response: Gio.AsyncResult) -> None:
            try:
                proxy.call_finish(response)
            except GLib.Error:
                logging.error(f"Failed to execute method {name}", exc_info=True)
                raise

        self.call(name, params, Gio.DBusCallFlags.NONE, -1, None, call_finish)


class DBus(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name="org.freedesktop.DBus", interface_name="org.freedesktop.DBus",
                         object_path="/org/freedesktop/DBus")


class Mechanism(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name='org.blueman.Mechanism', interface_name='org.blueman.Mechanism',
                         object_path="/org/blueman/mechanism", systembus=True)


class AppletService(ProxyBase):
    NAME = "org.blueman.Applet"

    def __init__(self) -> None:
        super().__init__(name=self.NAME, interface_name='org.blueman.Applet',
                         object_path="/org/blueman/Applet")


class AppletServiceApplication(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name=AppletService.NAME, interface_name="org.freedesktop.Application",
                         object_path="/org/blueman/Applet")

    def stop(self) -> None:
        self.ActivateAction('(sava{sv})', "Quit", [], {})


class ManagerService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name="org.blueman.Manager", interface_name="org.freedesktop.Application",
                         object_path="/org/blueman/Manager",
                         flags=Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION)

    def activate(self) -> None:
        try:
            param = GLib.Variant('(a{sv})', ({},))
            self.call_method("Activate", param)
        except GLib.Error:
            # This can different errors, depending on the system configuration, typically:
            # * org.freedesktop.DBus.Error.Spawn.ChildExited if dbus-daemon tries to launch the service itself.
            # * org.freedesktop.DBus.Error.NoReply if the systemd integration is used.
            Notification(
                _("Failed to reach blueman-manager"),
                _("It seems like blueman-manager could no get activated via D-Bus. "
                  "A typical cause for this is a broken graphical setup in the D-Bus activation environment "
                  "that can get resolved with a call to dbus-update-activation-environment, "
                  "typically issued from xinitrc (respectively the Sway config or similar)."),
                0,
            ).show()

    def _call_action(self, name: str) -> None:
        param = GLib.Variant('(sava{sv})', (name, [], {}))
        self.call_method('ActivateAction', param)

    def quit(self) -> None:
        self._call_action("Quit")
