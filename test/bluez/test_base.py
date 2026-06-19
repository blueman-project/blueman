from typing import Any, Optional
from unittest import TestCase
from unittest.mock import patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # noqa: E402

from blueman.bluemantyping import ObjectPath  # noqa: E402
from blueman.bluez.Base import Base, InstanceRegistry  # noqa: E402


class FakeVariant:
    """Minimal stand-in for GLib.Variant: only ``unpack()`` is used by Base."""

    def __init__(self, value: Any) -> None:
        self._value = value

    def unpack(self) -> Any:
        return self._value


class FakeProxy:
    """Fake Gio.DBusProxy counting sync round-trips and serving a cache."""

    def __init__(self, props: Optional[dict[str, Any]] = None,
                 object_path: str = "/org/test/dev0") -> None:
        self.props: dict[str, Any] = dict(props or {})
        self.cached: dict[str, Any] = dict(self.props)
        self.object_path = object_path
        self.sync_get_calls = 0
        self.sync_getall_calls = 0
        self.async_calls: list[tuple[str, Any]] = []
        self.get_should_raise: Optional[GLib.Error] = None
        self._pchanged_cb: Any = None

    def connect(self, signal: str, cb: Any) -> int:
        if signal == "g-properties-changed":
            self._pchanged_cb = cb
        return 1

    def get_object_path(self) -> str:
        return self.object_path

    def get_interface_name(self) -> str:
        return "org.test.Interface"

    def get_cached_property(self, name: str) -> Optional[FakeVariant]:
        if name in self.cached:
            return FakeVariant(self.cached[name])
        return None

    def call_sync(self, method: str, params: Any, *_args: Any) -> FakeVariant:
        _iface, *rest = params.unpack()
        if method == "org.freedesktop.DBus.Properties.Get":
            self.sync_get_calls += 1
            if self.get_should_raise is not None:
                raise self.get_should_raise
            return FakeVariant((self.props[rest[0]],))
        if method == "org.freedesktop.DBus.Properties.GetAll":
            self.sync_getall_calls += 1
            return FakeVariant((dict(self.props),))
        raise AssertionError(f"unexpected call_sync {method}")

    def call(self, method: str, params: Any, *_args: Any) -> None:
        self.async_calls.append((method, params))

    # Test helper: simulate a D-Bus PropertiesChanged signal.
    def emit_properties_changed(self, changed: dict[str, Any],
                                invalidated: Optional[list[str]] = None) -> None:
        self.cached.update(changed)
        self.props.update(changed)
        assert self._pchanged_cb is not None
        self._pchanged_cb(self, FakeVariant(changed), invalidated or [])


class FakeBase(Base):
    _interface_name = "org.test.Interface"


class OtherFakeBase(Base):
    _interface_name = "org.test.OtherInterface"


def make(cls: type, proxy: FakeProxy, path: str = "/org/test/dev0") -> Any:
    with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", return_value=proxy):
        return cls(obj_path=ObjectPath(path))


def _clear_registries() -> None:
    for cls in (FakeBase, OtherFakeBase):
        registry = cls.__dict__.get("_registry")
        if registry is not None:
            registry.clear()


class TestInstanceRegistry(TestCase):
    def test_add_get_remove_clear(self) -> None:
        reg = InstanceRegistry()
        sentinel = object()
        self.assertIsNone(reg.get("/p"))
        reg.add("/p", sentinel)  # type: ignore[arg-type]
        self.assertIs(reg.get("/p"), sentinel)
        reg.remove("/p")
        self.assertIsNone(reg.get("/p"))
        reg.add("/p", sentinel)  # type: ignore[arg-type]
        reg.clear()
        self.assertIsNone(reg.get("/p"))

    def test_remove_missing_is_noop(self) -> None:
        reg = InstanceRegistry()
        reg.remove("/absent")  # must not raise


class TestBaseInstanceCaching(TestCase):
    def setUp(self) -> None:
        _clear_registries()
        self.addCleanup(_clear_registries)

    def test_same_path_returns_same_instance(self) -> None:
        obj = make(FakeBase, FakeProxy(), "/org/test/dev0")
        again = make(FakeBase, FakeProxy(), "/org/test/dev0")
        self.assertIs(again, obj)

    def test_different_paths_distinct(self) -> None:
        a = make(FakeBase, FakeProxy(object_path="/org/test/a"), "/org/test/a")
        b = make(FakeBase, FakeProxy(object_path="/org/test/b"), "/org/test/b")
        self.assertIsNot(a, b)

    def test_registry_is_per_class(self) -> None:
        make(FakeBase, FakeProxy(), "/org/test/dev0")
        make(OtherFakeBase, FakeProxy(object_path="/org/test/dev0"), "/org/test/dev0")
        self.assertIsNot(FakeBase.__dict__.get("_registry"),
                         OtherFakeBase.__dict__.get("_registry"))

    def test_destroy_removes_from_registry(self) -> None:
        obj = make(FakeBase, FakeProxy(object_path="/org/test/dev0"), "/org/test/dev0")
        obj.destroy()
        replacement = make(FakeBase, FakeProxy(object_path="/org/test/dev0"), "/org/test/dev0")
        self.assertIsNot(replacement, obj)


class TestBasePropertyCache(TestCase):
    def setUp(self) -> None:
        _clear_registries()
        self.addCleanup(_clear_registries)

    def test_cached_read_avoids_sync_call(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        self.assertIs(obj.get("Connected"), True)
        self.assertEqual(proxy.sync_get_calls, 0)

    def test_repeated_cached_reads_stay_zero_round_trips(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        for _ in range(50):
            obj.get("Connected")
        self.assertEqual(proxy.sync_get_calls, 0)

    def test_cache_miss_falls_back_to_sync_get(self) -> None:
        proxy = FakeProxy()
        proxy.props["Address"] = "AA:BB:CC:DD:EE:FF"  # present live, absent from cache
        obj = make(FakeBase, proxy)
        self.assertEqual(obj.get("Address"), "AA:BB:CC:DD:EE:FF")
        self.assertEqual(proxy.sync_get_calls, 1)

    def test_properties_changed_refreshes_cache(self) -> None:
        proxy = FakeProxy({"Connected": False})
        obj = make(FakeBase, proxy)
        self.assertIs(obj.get("Connected"), False)
        proxy.emit_properties_changed({"Connected": True})
        self.assertIs(obj.get("Connected"), True)
        self.assertEqual(proxy.sync_get_calls, 0)

    def test_fallback_used_when_missing_and_sync_fails(self) -> None:
        proxy = FakeProxy()
        proxy.get_should_raise = GLib.Error.new_literal(GLib.quark_from_string("x"), "boom", 0)
        obj = make(FakeBase, proxy)
        self.assertEqual(obj.get("Icon"), "blueman")  # __fallback default

    def test_getitem_delegates_to_get(self) -> None:
        proxy = FakeProxy({"Paired": True})
        obj = make(FakeBase, proxy)
        self.assertIs(obj["Paired"], True)
