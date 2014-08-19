from blueman.Functions import dprint
from blueman.bluez.errors import raise_dbus_error, DBusServiceUnknownError
from blueman.main.SignalTracker import SignalTracker
import dbus
from gi.repository.GObject import GObject


class Base(GObject):
    interface_version = None

    @staticmethod
    def get_interface_version():
        if not Base.interface_version:
            @raise_dbus_error
            def lookup_object(bus_name, object_path):
                dbus.SessionBus().get_object(bus_name, object_path)

            try:
                lookup_object('org.bluez.obex', '/org/bluez/obex')
                dprint('Detected BlueZ integrated OBEX')
                Base.interface_version = [5]
            except DBusServiceUnknownError:
                try:
                    lookup_object('org.bluez.obex.client', '/')
                    dprint('Detected standalone OBEX')
                    Base.interface_version = [4]
                except DBusServiceUnknownError:
                    raise Exception("Could not find any compatible version of BlueZ's OBEX service")

        return Base.interface_version

    def __init__(self, obj_path, bus_name='org.bluez.obex'):
        self.__bus = dbus.SessionBus()
        self.__signals = SignalTracker()
        self.__dbus_proxy = self.__bus.get_object(bus_name, obj_path)
        super(Base, self).__init__()

    def _get_interface(self, interface):
        return dbus.Interface(self.__dbus_proxy, interface)

    def _get_bus(self):
        return self.__bus
