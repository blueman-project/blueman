from typing import Dict, List, Optional

from gi.repository import GObject, GLib
from gi.repository import Gio

from blueman.bluemantyping import GSignals


class AnyBase(GObject.GObject):
    __gsignals__: GSignals = {
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None, (str, object, str))
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus_name = 'org.bluez'
    __bus_interface_name = 'org.freedesktop.DBus.Properties'

    def __init__(self, interface_name: str):
        super().__init__()

        self.__bus: Optional[Gio.DBusConnection] = Gio.bus_get_sync(Gio.BusType.SYSTEM)

        self.__interface_name = interface_name
        self.__signal = None

        def on_signal(
            _connection: Gio.DBusConnection,
            _sender_name: str,
            object_path: str,
            _interface_name: str,
            _signal_name: str,
            param: GLib.Variant,
        ) -> None:
            iface_name, changed, invalidated = param.unpack()
            if iface_name == self.__interface_name:
                self._on_properties_changed(object_path, changed, invalidated)

        self.__signal = self.__bus.signal_subscribe(
            self.__bus_name, self.__bus_interface_name, 'PropertiesChanged', None, None,
            Gio.DBusSignalFlags.NONE, on_signal)

    def _on_properties_changed(
        self, object_path: str, changed_properties: Dict[str, object], _invalidated: List[str]
    ) -> None:
        for name, value in changed_properties.items():
            self.emit('property-changed', name, value, object_path)

    def close(self) -> None:
        if self.__signal:
            if self.__bus is not None:
                self.__bus.signal_unsubscribe(self.__signal)
            self.__signal = None
        self.__bus = None
