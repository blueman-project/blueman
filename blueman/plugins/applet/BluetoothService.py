from collections.abc import Callable
from gettext import gettext as _

from blueman.bluez.Adapter import Adapter
from blueman.bluez.errors import BluezDBusException, parse_dbus_error
from blueman.main.Applet import BluemanApplet
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluemantyping import ObjectPath

from gi.repository import GLib


class BluetoothService(AppletPlugin):
    __depends__ = ["DBusService"]
    __unloadable__ = False
    __description__ = _("Handles BlueZ services")
    __author__ = "infirit"
    __icon__ = "blueman"
    __dbus_iface_name__ = "org.blueman.Applet.Bluetooth"

    def __init__(self, parent: BluemanApplet) -> None:
        super().__init__(parent)
        self._discovering = False

    def on_load(self) -> None:
        self._add_dbus_method("StartDiscovery", ("o", "i",), "", self._start_discovery, is_async=True)
        self._add_dbus_method("StopDiscovery", ("o",), "", self._stop_discovery, is_async=True)
        self._add_dbus_signal("Discovering", "b")

    def _start_discovery(
            self,
            object_path: ObjectPath,
            discover_timeout: int,
            ok: Callable[[str], None],
            err: Callable[[BluezDBusException], None]
    ) -> None:

        if self._discovering:
            ok(f"Already discovering {object_path}")
            return

        try:
            adapter = Adapter(obj_path=object_path)
            adapter.start_discovery()
            self._discovering = True
            ok(f"Discovering {object_path}")
        except GLib.Error as e:
            err(parse_dbus_error(e))
            return


    def _stop_discovery(self,
            object_path: ObjectPath,
            ok: Callable[[str], None],
            err: Callable[[BluezDBusException], None]
    ) -> None:

        if not self._discovering:
            ok("Not discovering")

        try:
            adapter = Adapter(obj_path=object_path)
            adapter.stop_discovery()
            ok(f"Stopped discovery {object_path}")
        except GLib.Error as e:
            err(parse_dbus_error(e))
            return
