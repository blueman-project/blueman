from typing import Iterable, cast
from gettext import gettext as _
import logging

from gi.repository import Gio, GLib

from blueman.gobject import SingletonGObjectMeta
from blueman.gui.Notification import Notification
from blueman.plugins.applet.Menu import MenuItemDict
from blueman.bluemantyping import ObjectPath


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

    def call_method(self, name: str, params: GLib.Variant | None) -> None:
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
    PATH = "/org/blueman/Applet"

    def __init__(self, interface_name: str = "org.blueman.Applet") -> None:
        super().__init__(name=self.NAME, interface_name=interface_name,
                         object_path=self.PATH)


class AppletPowerManagerService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name=AppletService.NAME, interface_name="org.blueman.Applet.PowerManager",
                         object_path=AppletService.PATH)

    def get_bluetooth_status(self) -> bool:
        result = self.call_sync("org.blueman.Applet.PowerManager.GetBluetoothStatus", None,
                                Gio.DBusCallFlags.NONE, -1, None)
        value = cast(bool, result.unpack()[0])
        return value

    def set_bluetooth_status(self, status: bool) -> None:
        param = GLib.Variant("(b)", (status, ))
        self.call_sync("org.blueman.Applet.PowerManager.SetBluetoothStatus", param, Gio.DBusCallFlags.NONE, -1, None)


class AppletDhcpClientService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name=AppletService.NAME, interface_name="org.blueman.Applet.DhcpClient",
                         object_path=AppletService.PATH)

    def dchp_client(self, object_path: ObjectPath) -> None:
        param = GLib.Variant("o", object_path)
        self.call_sync("org.blueman.Applet.DhcpClient.DhcpClient", param, Gio.DBusCallFlags.NONE, -1, None)


class AppletMenuService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name=AppletService.NAME, interface_name="org.blueman.Applet.Menu",
                         object_path=AppletService.PATH)

    def get_menu(self) -> Iterable[MenuItemDict]:
        result = self.call_sync("GetMenu", None, Gio.DBusCallFlags.NONE, -1, None)
        value = cast(Iterable[MenuItemDict], result.unpack()[0])
        return value

    def get_statusicon_implementations(self) -> list[str]:
        result = self.call_sync("org.blueman.Applet.StatusIcon.GetStatusIconImplementations", None,
                                Gio.DBusCallFlags.NONE, -1, None)
        value = cast(list[str], result.unpack()[0])
        return value

    def get_icon_name(self) -> str:
        result = self.call_sync("org.blueman.Applet.StatusIcon.GetIconName", None, Gio.DBusCallFlags.NONE, -1, None)
        value = cast(str, result.unpack()[0])
        return value

    def get_tooltip_title(self) -> str:
        result = self.call_sync("org.blueman.Applet.StatusIcon.GetToolTipTitle", None, Gio.DBusCallFlags.NONE, -1, None)
        value = cast(str, result.unpack()[0])
        return value

    def get_tooltip_text(self) -> str:
        result = self.call_sync("org.blueman.Applet.StatusIcon.GetToolTipText", None, Gio.DBusCallFlags.NONE, -1, None)
        value = cast(str, result.unpack()[0])
        return value

    def get_visibility(self) -> bool:
        result = self.call_sync("org.blueman.Applet.StatusIcon.GetVisibility", None, Gio.DBusCallFlags.NONE, -1, None)
        value = cast(bool, result.unpack()[0])
        return value


class AppletStatusIconService(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name=AppletService.NAME, interface_name="org.blueman.Applet.StatusIcon",
                         object_path=AppletService.PATH)


class AppletServiceApplication(ProxyBase):
    def __init__(self) -> None:
        super().__init__(name=AppletService.NAME, interface_name="org.freedesktop.Application",
                         object_path=AppletService.PATH)

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
