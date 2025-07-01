from unittest import TestCase

from gi.repository import GLib, Gio

from blueman.main.indicators.StatusNotifierItem import is_service_unknown


class TestGDbusError(TestCase):
    def test_is_service_unknown(self):
        error = None

        try:
            Gio.bus_get_sync(Gio.BusType.SESSION).call_sync(
                "some.name", "/some/path", "some.Interface",
                "SomeMethod", GLib.Variant("()", ()),
                None, Gio.DBusCallFlags.NONE, -1)
        except GLib.Error as e:
            error = e

        self.assertTrue(is_service_unknown(error))
