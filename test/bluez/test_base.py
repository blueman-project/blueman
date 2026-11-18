from typing import Any, Optional
from unittest import TestCase
from unittest.mock import patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # noqa: E402

from blueman.bluemantyping import ObjectPath  # noqa: E402
from blueman.bluez.Base import Base, InstanceRegistry  # noqa: E402
from blueman.bluez.errors import BluezDBusException  # noqa: E402


class FakeVariant:
    """Minimal stand-in for GLib.Variant: only ``unpack()`` is used by Base."""

    def __init__(self, value: Any) -> None:
        self._value = value

    def unpack(self) -> Any:
        return self._value


class FakeAsyncResult:
    def __init__(self, value: tuple, error: "Optional[GLib.Error]") -> None:
        self.value = value
        self.error = error


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
        self._last_async: tuple[Any, Any, Any] = (None, None, None)

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
            if rest[0] not in self.props:
                raise GLib.Error.new_literal(
                    GLib.quark_from_string("g-dbus-error-quark"),
                    "GDBus.Error:org.bluez.Error.DoesNotExist:No such property", 0)
            return FakeVariant((self.props[rest[0]],))
        if method == "org.freedesktop.DBus.Properties.GetAll":
            self.sync_getall_calls += 1
            return FakeVariant((dict(self.props),))
        raise AssertionError(f"unexpected call_sync {method}")

    def call(self, method: str, params: Any, _flags: Any = None, _timeout: Any = None,
             _cancellable: Any = None, callback: Any = None, reply: Any = None,
             error: Any = None) -> None:
        self.async_calls.append((method, params))
        self._last_async = (callback, reply, error)

    def call_finish(self, result: "FakeAsyncResult") -> FakeVariant:
        if result.error is not None:
            raise result.error
        return FakeVariant(result.value)

    # Test helper: fire the most recent async .call() callback.
    def fire_last(self, value: tuple = (), raise_error: Optional[GLib.Error] = None) -> None:
        callback, reply, error = self._last_async
        if callback is None:
            return
        callback(self, FakeAsyncResult(value, raise_error), reply, error)

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

    def test_disconnect_signal_reflected_without_sync(self) -> None:
        # A device disconnect (manual or link loss) arrives as a
        # PropertiesChanged(Connected=false); the cached read must observe it
        # immediately and without a synchronous round-trip.
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        self.assertIs(obj.get("Connected"), True)
        proxy.emit_properties_changed({"Connected": False})
        self.assertIs(obj.get("Connected"), False)
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


class TestBaseCacheFreshness(TestCase):
    def setUp(self) -> None:
        _clear_registries()
        self.addCleanup(_clear_registries)

    def _err(self) -> GLib.Error:
        return GLib.Error.new_literal(GLib.quark_from_string("x"), "bus down", 0)

    def test_fresh_forces_sync_even_when_cached(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        obj.get("Connected", fresh=True)
        self.assertEqual(proxy.sync_get_calls, 1)

    def test_not_stale_by_default(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        obj.get("Connected")
        self.assertFalse(obj.is_stale("Connected"))

    def test_failed_fresh_serves_cache_and_marks_stale(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        proxy.get_should_raise = self._err()
        self.assertIs(obj.get("Connected", fresh=True), True)  # served from cache
        self.assertTrue(obj.is_stale("Connected"))

    def test_properties_changed_clears_stale(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        proxy.get_should_raise = self._err()
        obj.get("Connected", fresh=True)
        self.assertTrue(obj.is_stale("Connected"))
        proxy.emit_properties_changed({"Connected": False})
        self.assertFalse(obj.is_stale("Connected"))

    def test_successful_sync_clears_stale(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        proxy.get_should_raise = self._err()
        obj.get("Connected", fresh=True)
        self.assertTrue(obj.is_stale("Connected"))
        proxy.get_should_raise = None
        obj.get("Connected", fresh=True)
        self.assertFalse(obj.is_stale("Connected"))

    def test_logs_debug_when_serving_cache_after_error(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        proxy.get_should_raise = self._err()
        with self.assertLogs(level="DEBUG") as cm:
            obj.get("Connected", fresh=True)
        self.assertTrue(any("serving cached value after" in m for m in cm.output))


class TestBaseMisc(TestCase):
    def setUp(self) -> None:
        _clear_registries()
        self.addCleanup(_clear_registries)

    def test_set_issues_async_call(self) -> None:
        proxy = FakeProxy()
        obj = make(FakeBase, proxy)
        obj.set("Trusted", True)
        self.assertEqual(proxy.async_calls[-1][0], "org.freedesktop.DBus.Properties.Set")

    def test_setitem_delegates_to_set(self) -> None:
        proxy = FakeProxy()
        obj = make(FakeBase, proxy)
        obj["Alias"] = "phone"
        self.assertEqual(proxy.async_calls[-1][0], "org.freedesktop.DBus.Properties.Set")

    def test_get_properties_includes_fallback(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        props = obj.get_properties()
        self.assertIs(props["Connected"], True)
        self.assertEqual(props["Icon"], "blueman")  # fallback filled in

    def test_contains_uses_get_properties(self) -> None:
        proxy = FakeProxy({"Connected": True})
        obj = make(FakeBase, proxy)
        self.assertIn("Connected", obj)
        self.assertNotIn("Nonexistent", obj)

    def test_get_object_path(self) -> None:
        proxy = FakeProxy(object_path="/org/test/dev0")
        obj = make(FakeBase, proxy)
        self.assertEqual(obj.get_object_path(), "/org/test/dev0")

    def test_call_dispatches_async(self) -> None:
        proxy = FakeProxy()
        obj = make(FakeBase, proxy)
        obj._call("Connect")
        self.assertEqual(proxy.async_calls[-1][0], "Connect")

    def test_call_reply_handler_receives_value(self) -> None:
        proxy = FakeProxy()
        obj = make(FakeBase, proxy)
        got: list[Any] = []
        obj._call("Connect", reply_handler=lambda *a: got.append(a))
        proxy.fire_last(value=(1, 2))
        self.assertEqual(got, [(1, 2)])

    def test_call_error_handler_receives_bluez_error(self) -> None:
        proxy = FakeProxy()
        obj = make(FakeBase, proxy)
        errs: list[Any] = []
        obj._call("Connect", error_handler=errs.append)
        proxy.fire_last(raise_error=GLib.Error.new_literal(
            GLib.quark_from_string("x"), "GDBus.Error:org.bluez.Error.Failed:nope", 0))
        self.assertEqual(len(errs), 1)
        self.assertIsInstance(errs[0], BluezDBusException)

    def test_call_unhandled_error_is_logged(self) -> None:
        proxy = FakeProxy()
        obj = make(FakeBase, proxy)
        obj._call("Connect")
        with self.assertLogs(level="ERROR") as cm:
            proxy.fire_last(raise_error=GLib.Error.new_literal(
                GLib.quark_from_string("x"), "GDBus.Error:org.bluez.Error.Failed:nope", 0))
        self.assertTrue(any("Unhandled error" in m for m in cm.output))

    def test_get_properties_keeps_present_fallback_key(self) -> None:
        proxy = FakeProxy({"Icon": "phone", "Connected": True})
        obj = make(FakeBase, proxy)
        props = obj.get_properties()
        self.assertEqual(props["Icon"], "phone")  # not overwritten by fallback

    def test_properties_changed_emits_signal(self) -> None:
        proxy = FakeProxy({"Connected": False})
        obj = make(FakeBase, proxy)
        seen: list[tuple[str, Any]] = []
        obj.connect_signal("property-changed", lambda _o, k, v, _p: seen.append((k, v)))
        proxy.emit_properties_changed({"Connected": True})
        self.assertIn(("Connected", True), seen)


class TestBaseFuzz(TestCase):
    """Adversarial inputs to the read/refresh paths must never raise unexpectedly."""

    def setUp(self) -> None:
        _clear_registries()
        self.addCleanup(_clear_registries)

    def test_get_arbitrary_names_only_raises_bluez_error(self) -> None:
        known = {"Connected": True, "Class": 0, "Icon": "blueman"}
        proxy = FakeProxy(dict(known))
        obj = make(FakeBase, proxy)
        names = [
            "", " ", "\t", "\n", "Connected", "UUIDs", "x" * 4096, "na/me",
            "Conn:ected", "0", "../etc", "Ünïcode", "drop;table", "%s%n",
        ]
        for i, name in enumerate(names):
            with self.subTest(name=name):
                try:
                    obj.get(name, fresh=bool(i % 2))
                except BluezDBusException:
                    pass  # acceptable: unknown property over the bus

    def test_properties_changed_arbitrary_payloads_never_raise(self) -> None:
        proxy = FakeProxy({"Connected": True})
        make(FakeBase, proxy)  # connects proxy to the handler under test
        payloads = [
            {}, {"A": 1}, {"": None}, {"x" * 1000: "y" * 1000},
            {"Ünïcode": "✓", "n\x00ul": 1},
        ]
        invalidateds = [[], ["A"], ["", "B"], ["x" * 1000]]
        for i, changed in enumerate(payloads):
            with self.subTest(i=i):
                proxy.emit_properties_changed(changed, invalidateds[i % len(invalidateds)])
