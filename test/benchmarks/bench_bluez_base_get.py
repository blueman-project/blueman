"""Benchmark for the bluez Base property-read path (perf-4).

Before perf-4, ``Base.get`` issued one synchronous ``Properties.Get`` D-Bus
round-trip on every read. After perf-4 it serves from the proxy's local cache
(kept current by PropertiesChanged), so repeated reads of the same property
cost zero round-trips.

Each ``call_sync`` models one synchronous D-Bus round-trip (the dominant cost
on this blocking path). Output is one JSON line comparing modeled round-trips
for the old "always sync" behaviour against the current cached-first ``get``.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib  # noqa: E402

_constants = types.ModuleType("blueman.Constants")
for _name in ("BIN_DIR", "BLUETOOTHD_PATH", "ICON_PATH", "PIXMAP_PATH", "UI_PATH"):
    setattr(_constants, _name, Path("/tmp"))
sys.modules.setdefault("blueman.Constants", _constants)

from blueman.bluemantyping import ObjectPath  # noqa: E402
from blueman.bluez.Base import Base  # noqa: E402

# Cost of one synchronous D-Bus round-trip on the system bus; conservative.
DBUS_RTT = 0.0002  # 200 microseconds

# A device row reads this many properties repeatedly while the manager is open.
PROPS = ["Connected", "Paired", "Trusted", "Blocked", "Icon", "Class", "Address"]


class CountingVariant:
    def __init__(self, value: Any) -> None:
        self._value = value

    def unpack(self) -> Any:
        return self._value


class CountingProxy:
    """Fake proxy counting synchronous round-trips, with a warm cache."""

    def __init__(self, props: dict[str, Any]) -> None:
        self._props = props
        self._cached = dict(props)  # warm, as Gio loads + signal-updates it
        self.sync_calls = 0

    def connect(self, *_args: Any) -> int:
        return 1

    def get_object_path(self) -> str:
        return "/org/bluez/hci0/dev_AA"

    def get_interface_name(self) -> str:
        return "org.bluez.Device1"

    def get_cached_property(self, name: str) -> CountingVariant | None:
        if name in self._cached:
            return CountingVariant(self._cached[name])
        return None

    def call_sync(self, _method: str, params: Any, *_a: Any) -> CountingVariant:
        self.sync_calls += 1
        name = params.unpack()[1]
        return CountingVariant((self._props[name],))


class FakeBase(Base):
    _interface_name = "org.bluez.Device1"


def run(reads_per_prop: int) -> dict[str, Any]:
    props = {p: (True if p in ("Connected", "Paired", "Trusted", "Blocked") else "x") for p in PROPS}
    proxy = CountingProxy(props)
    with patch("blueman.bluez.Base.Gio.DBusProxy.new_for_bus_sync", return_value=proxy):
        obj = FakeBase(obj_path=ObjectPath("/org/bluez/hci0/dev_AA"))

    total_reads = reads_per_prop * len(PROPS)
    for _ in range(reads_per_prop):
        for p in PROPS:
            obj.get(p)

    new_roundtrips = proxy.sync_calls          # cached-first: expected 0
    old_roundtrips = total_reads               # always-sync: one per read
    return {
        "reads": total_reads,
        "old_roundtrips": old_roundtrips,
        "new_roundtrips": new_roundtrips,
        "dbus_rtt": DBUS_RTT,
        "old_modeled_seconds": old_roundtrips * DBUS_RTT,
        "new_modeled_seconds": new_roundtrips * DBUS_RTT,
        "roundtrips_saved_pct": (old_roundtrips - new_roundtrips) / old_roundtrips * 100,
    }


def _silence_glib_unused() -> None:
    # GLib imported for parity with the module under test / future use.
    assert GLib is not None


if __name__ == "__main__":
    _silence_glib_unused()
    reads = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(json.dumps(run(reads)))
