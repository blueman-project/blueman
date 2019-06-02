from gi.repository import GObject
from gi.repository import Gio


class AnyBase(GObject.GObject):
    __gsignals__ = {
        'property-changed': (GObject.SignalFlags.NO_HOOKS, None,
                             (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT))
    }

    connect_signal = GObject.GObject.connect
    disconnect_signal = GObject.GObject.disconnect

    __bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)
    __bus_name = 'org.bluez'
    __bus_interface_name = 'org.freedesktop.DBus.Properties'

    def __init__(self, interface_name):
        super().__init__()

        self.__interface_name = interface_name
        self.__signal = None

        def on_signal(_connection, _sender_name, object_path, _interface_name, _signal_name, param):
            iface_name, changed, invalidated = param.unpack()
            if iface_name == self.__interface_name:
                self._on_properties_changed(object_path, changed, invalidated)

        self.__signal = self.__bus.signal_subscribe(
            self.__bus_name, self.__bus_interface_name, 'PropertiesChanged', None, None,
            Gio.DBusSignalFlags.NONE, on_signal)

    def _on_properties_changed(self, object_path, changed_properties, invalidated):
        for name, value in changed_properties.items():
            self.emit('property-changed', name, value, object_path)

    def close(self):
        if self.__signal:
            self.__bus.signal_unsubscribe(self.__signal)
            self.__signal = None
        self.__bus = None
