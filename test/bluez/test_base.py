import gc
import weakref
from unittest import TestCase
from unittest.mock import patch

from blueman.bluemantyping import ObjectPath
from blueman.bluez.Base import Base
from gi.repository import Gio


class FakeProxy:
    def __init__(self, object_path: str = "/org/test/fake") -> None:
        self.calls = []
        self.object_path = object_path

    def connect(self, *_args):
        return 1

    def call(self, *args):
        self.calls.append(args)

    def call_finish(self, _result):
        return None

    def get_interface_name(self):
        return "org.test.Interface"

    def get_object_path(self):
        return self.object_path


class TestBaseObject(Base):
    _interface_name = "org.test.Interface"


class OtherTestBaseObject(Base):
    _interface_name = "org.test.OtherInterface"


class TestBaseConcurrency(TestCase):
    def setUp(self):
        for cls in (TestBaseObject, OtherTestBaseObject):
            if hasattr(cls, "__instances__"):
                cls.__instances__.clear()

    def test_instance_cache_uses_weak_values(self):
        with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", return_value=FakeProxy()):
            obj = TestBaseObject(obj_path=ObjectPath("/org/test/device0"))
            self.assertIs(TestBaseObject(obj_path=ObjectPath("/org/test/device0")), obj)
            obj_ref = weakref.ref(obj)

            del obj
            gc.collect()

        self.assertIsNone(obj_ref())

    def test_instance_cache_is_per_subclass(self):
        with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", return_value=FakeProxy()):
            obj = TestBaseObject(obj_path=ObjectPath("/org/test/shared"))
            other = OtherTestBaseObject(obj_path=ObjectPath("/org/test/shared"))

        self.assertIsNot(obj, other)

    def test_destroy_removes_instance_from_cache(self):
        with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync") as new_proxy:
            new_proxy.side_effect = [FakeProxy("/org/test/destroyed"), FakeProxy("/org/test/destroyed")]
            obj = TestBaseObject(obj_path=ObjectPath("/org/test/destroyed"))

            obj.destroy()
            next_obj = TestBaseObject(obj_path=ObjectPath("/org/test/destroyed"))

        self.assertIsNot(obj, next_obj)

    def test_set_passes_cancellable_to_dbus_call(self):
        proxy = FakeProxy()
        cancellable = Gio.Cancellable()

        with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", return_value=proxy):
            obj = TestBaseObject(obj_path=ObjectPath("/org/test/device1"))
            obj.set("Powered", True, cancellable=cancellable)

        call = proxy.calls[0]
        self.assertEqual(call[0], "org.freedesktop.DBus.Properties.Set")
        self.assertIs(call[4], cancellable)
        self.assertIs(call[6], cancellable)

    def test_destroy_cancels_pending_set_calls(self):
        cancellable = Gio.Cancellable()

        with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", return_value=FakeProxy()):
            obj = TestBaseObject(obj_path=ObjectPath("/org/test/device2"))
            obj.set("Powered", True, cancellable=cancellable)

            obj.destroy()

        self.assertTrue(cancellable.is_cancelled())
