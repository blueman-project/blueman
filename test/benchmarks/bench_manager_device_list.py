"""Micro-benchmark for ManagerDeviceList row setup/update hot paths.

The optimization under test collapses many per-property D-Bus reads
(``device["Key"]`` -> ``org.freedesktop.DBus.Properties.Get``) into a single
``device.get_properties()`` call (``Properties.GetAll``) plus cached liststore
state. Each ``__getitem__`` and each ``get_properties()`` therefore models one
synchronous D-Bus round-trip -- the dominant real-world cost on this path.

The benchmark is version-agnostic: it drives whichever ``ManagerDeviceList`` is
importable from the current tree, so the same file runs against both ``main``
and the optimized branch (see ``run_compare.sh``).

Output: a single JSON line with round-trip counts and a modeled wall time
(pure-Python CPU time + round-trips * DBUS_RTT).
"""
from __future__ import annotations

import inspect
import json
import logging
import sys
import time
import types
from pathlib import Path
from unittest.mock import Mock

import gi

gi.require_version("Gtk", "3.0")  # must precede ManagerDeviceList import

# Stub blueman.Constants the same way the unit tests do, so importing the
# module under test never touches the real installation paths.
_constants = types.ModuleType("blueman.Constants")
_constants.BIN_DIR = Path("/tmp")
_constants.BLUETOOTHD_PATH = Path("/tmp/bluetoothd")
_constants.ICON_PATH = Path("/tmp")
_constants.PIXMAP_PATH = Path("/tmp")
_constants.UI_PATH = Path("/tmp")
sys.modules.setdefault("blueman.Constants", _constants)

from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList  # noqa: E402

# Modeled cost of one synchronous D-Bus round-trip (Properties.Get / GetAll via
# Gio call_sync) on a local system bus. Conservative; the relative gain is
# insensitive to the exact value because it is dominated by round-trip count.
DBUS_RTT = 0.0002  # 200 microseconds

# Keys updated after initial setup, mirroring real signal traffic. "Connected"
# is intentionally excluded so neither version enters the power-level timer
# machinery -- keeping the comparison focused on the property-read path.
UPDATE_KEYS: list[tuple[str, object]] = [
    ("Trusted", True),
    ("Paired", True),
    ("Blocked", False),
    ("Alias", "Keyboard"),
    ("UUIDs", ["00001105-0000-1000-8000-00805f9b34fb"]),
]


class CountingDevice:
    """Fake bluez Device that counts simulated D-Bus round-trips."""

    display_name = "Keyboard"

    def __init__(self, counters: dict[str, int]) -> None:
        self._counters = counters
        self.properties = {
            "Address": "AA:BB:CC:DD:EE:FF",
            "Alias": "Keyboard",
            "Appearance": 0,
            "Blocked": False,
            "Class": 0,
            "Connected": False,
            "Icon": "input-keyboard",
            "Paired": False,
            "Trusted": False,
            "UUIDs": ["00001105-0000-1000-8000-00805f9b34fb"],
        }

    def __getitem__(self, key: str) -> object:
        self._counters["roundtrips"] += 1  # Properties.Get
        return self.properties[key]

    def get_properties(self) -> dict[str, object]:
        self._counters["roundtrips"] += 1  # Properties.GetAll
        return dict(self.properties)

    def get_object_path(self) -> str:
        return "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"


class Harness:
    """Minimal stand-in for ManagerDeviceList state.

    Only GTK/render primitives are faked; the methods under test
    (``row_setup_event``, ``row_update_event``, ``_has_objpush``,
    ``get_device_class``) are the real ones, bound below.
    """

    Adapter = None
    filter = Mock()

    def __init__(self, counters: dict[str, int]) -> None:
        self.values: dict[str, object] = {
            "initial_anim": True,
            "device": CountingDevice(counters),
            "objpush": False,
            "uuids": (),
        }
        self._monitored_devices: set[str] = set()
        self._power_levels_timer = None

    def get(self, _tree_iter: object, *keys: str) -> dict[str, object]:
        return {key: self.values[key] for key in keys}

    def set(self, _tree_iter: object, **kwargs: object) -> None:
        self.values.update(kwargs)

    def _make_device_icon(self, *_args: object) -> object:
        # Cheap stand-in for a cairo surface; SurfaceObject only stores it.
        return None

    def _disable_power_levels(self, _tree_iter: object) -> None:
        pass

    def make_display_name(self, display_name: str, _klass: object, _address: object) -> str:
        return display_name

    def make_caption(self, display_name: str, description: str, address: object) -> str:
        return f"{display_name} {description} {address}"

    # Real implementations under test, copied as the *original descriptors*
    # (staticmethod vs plain function) so each version binds correctly:
    # main's _has_objpush is an instance method, the branch's is static.
    _has_objpush = inspect.getattr_static(ManagerDeviceList, "_has_objpush")
    get_device_class = inspect.getattr_static(ManagerDeviceList, "get_device_class")
    row_setup_event = inspect.getattr_static(ManagerDeviceList, "row_setup_event")
    row_update_event = inspect.getattr_static(ManagerDeviceList, "row_update_event")


def _one_pass(counters: dict[str, int]) -> None:
    harness = Harness(counters)
    tree_iter = object()
    harness.row_setup_event(tree_iter, harness.values["device"])
    for key, value in UPDATE_KEYS:
        harness.row_update_event(tree_iter, key, value)


def run(iterations: int) -> dict[str, object]:
    logging.disable(logging.CRITICAL)  # silence per-update info logging

    # Warm up (import/JIT of attribute caches) without scoring it.
    _one_pass({"roundtrips": 0})

    counters = {"roundtrips": 0}
    start = time.perf_counter()
    for _ in range(iterations):
        _one_pass(counters)
    cpu = time.perf_counter() - start

    roundtrips = counters["roundtrips"]
    modeled = cpu + roundtrips * DBUS_RTT
    return {
        "iterations": iterations,
        "roundtrips_total": roundtrips,
        "roundtrips_per_iter": roundtrips / iterations,
        "cpu_seconds": cpu,
        "dbus_rtt": DBUS_RTT,
        "modeled_seconds": modeled,
    }


if __name__ == "__main__":
    iters = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    print(json.dumps(run(iters)))
