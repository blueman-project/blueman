from unittest import TestCase
from unittest.mock import Mock, patch

from gi.repository import Gio, GLib

from blueman.bluemantyping import BtAddress, ObjectPath
from blueman.bluez.Device import Device
from blueman.bluez.Manager import Manager
from blueman.gobject import SingletonGObjectMeta


class TestManager(TestCase):
    def test_metaclass(self):
        self.assertIsInstance(Manager, SingletonGObjectMeta)


ADDRESSES = {
    "/org/bluez/hci0": "00:00:00:00:00:01",
    "/org/bluez/hci0/dev_AA_AA_AA_AA_AA_AA": "AA:AA:AA:AA:AA:AA",
    "/org/bluez/hci1/dev_BB_BB_BB_BB_BB_BB": "BB:BB:BB:BB:BB:BB",
    "/org/bluez/hci1/dev_CC_CC_CC_CC_CC_CC": None,
}


class FakeDBusObject:
    def __init__(self, interface: str, path: str) -> None:
        self._proxy = Gio.DBusProxy(g_name="org.bluez", g_object_path=path, g_interface_name=interface,
                                    g_flags=Gio.DBusProxyFlags.DO_NOT_LOAD_PROPERTIES)

    def get_interface(self, name: str) -> Gio.DBusProxy | None:
        return self._proxy if name == self._proxy.get_interface_name() else None


def device_proxy(*args: object) -> Mock:
    path = args[4]
    address = ADDRESSES[path]
    proxy = Mock()
    proxy.get_object_path.return_value = path
    proxy.get_cached_property.side_effect = \
        lambda name: GLib.Variant("s", address) if name == "Address" and address else None
    proxy.call_sync.side_effect = AssertionError("find_device made a blocking D-Bus call")
    return proxy


class TestFindDevice(TestCase):
    def setUp(self) -> None:
        object_manager = Mock()
        object_manager.get_objects.return_value = [
            FakeDBusObject("org.bluez.Adapter1", "/org/bluez/hci0"),
            FakeDBusObject("org.bluez.Device1", "/org/bluez/hci0/dev_AA_AA_AA_AA_AA_AA"),
            FakeDBusObject("org.bluez.Device1", "/org/bluez/hci1/dev_BB_BB_BB_BB_BB_BB"),
            FakeDBusObject("org.bluez.Device1", "/org/bluez/hci1/dev_CC_CC_CC_CC_CC_CC"),
        ]

        self.addCleanup(setattr, Manager, "_instance", Manager._instance)
        Manager._instance = None
        with patch("blueman.bluez.Manager.Gio.DBusObjectManagerClient.new_for_bus_sync", return_value=object_manager):
            self.manager = Manager()

        # Base caches one Device per object path; start each test without the fakes of another.
        self.addCleanup(Device.__dict__.get("__instances__", {}).clear)
        Device.__dict__.get("__instances__", {}).clear()
        proxy_patch = patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", side_effect=device_proxy)
        proxy_patch.start()
        self.addCleanup(proxy_patch.stop)

    def test_returns_matching_device(self) -> None:
        found = self.manager.find_device(BtAddress("BB:BB:BB:BB:BB:BB"))

        assert found is not None
        self.assertEqual(found.get_object_path(), "/org/bluez/hci1/dev_BB_BB_BB_BB_BB_BB")

    def test_limits_search_to_adapter(self) -> None:
        self.assertIsNone(self.manager.find_device(BtAddress("BB:BB:BB:BB:BB:BB"), ObjectPath("/org/bluez/hci0")))

    def test_ignores_adapter_address(self) -> None:
        self.assertIsNone(self.manager.find_device(BtAddress("00:00:00:00:00:01")))

    def test_unknown_address(self) -> None:
        self.assertIsNone(self.manager.find_device(BtAddress("DD:DD:DD:DD:DD:DD")))
