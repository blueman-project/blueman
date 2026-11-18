"""Benchmark for DeviceList.clear() (perf-3 and vec-3).

Three strategies on a real Gtk.ListStore plus a path_to_row cache of one live
Gtk.TreeRowReference per row (as DeviceList keeps):

- original : remove each row individually (each delete validates the iter and
             updates every live reference) and then clear() — two O(n^2) passes
             plus a mutation-while-iterating bug.
- perf-3   : a single liststore.clear() while the references are still alive —
             drops the redundant per-row loop, but clear() must still update
             every live reference, so it is still ~O(n^2).
- vec-3    : release the reference cache *before* clear() so GTK has nothing to
             keep in sync — clear() becomes ~O(n).

Output is one JSON blob with per-size timings and the 2x growth factor for each
strategy (~4 means quadratic, ~2 means linear).
"""
from __future__ import annotations

import json
import sys
import time

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

SIZES = [500, 1000, 2000, 4000]


def _populate(n: int) -> tuple[Gtk.ListStore, dict[str, Gtk.TreeRowReference]]:
    store = Gtk.ListStore(str)
    refs: dict[str, Gtk.TreeRowReference] = {}
    for i in range(n):
        path = f"/org/bluez/hci0/dev_{i}"
        tree_iter = store.append([path])
        refs[path] = Gtk.TreeRowReference.new(store, store.get_path(tree_iter))
    return store, refs


def _original(store: Gtk.ListStore, refs: dict[str, Gtk.TreeRowReference]) -> None:
    for path in list(refs):
        ref = refs[path]
        if ref.valid():
            tree_path = ref.get_path()
            assert tree_path is not None
            store.remove(store.get_iter(tree_path))
        del refs[path]
    store.clear()


def _perf3(store: Gtk.ListStore, refs: dict[str, Gtk.TreeRowReference]) -> None:
    store.clear()
    refs.clear()


def _vec3(store: Gtk.ListStore, refs: dict[str, Gtk.TreeRowReference]) -> None:
    refs.clear()
    store.clear()


STRATEGIES = {"original": _original, "perf3": _perf3, "vec3": _vec3}


def run() -> dict[str, object]:
    timings: dict[str, list[float]] = {name: [] for name in STRATEGIES}
    for n in SIZES:
        for name, fn in STRATEGIES.items():
            store, refs = _populate(n)
            start = time.perf_counter()
            fn(store, refs)
            timings[name].append(time.perf_counter() - start)

    def growth(name: str) -> float:
        t = timings[name]
        return t[-1] / t[-2] if t[-2] else float("inf")

    return {
        "sizes": SIZES,
        "seconds": {name: [round(t, 6) for t in ts] for name, ts in timings.items()},
        "growth_2x": {name: round(growth(name), 2) for name in STRATEGIES},
        "vec3_speedup_vs_original_at_max": round(
            timings["original"][-1] / timings["vec3"][-1], 1),
    }


if __name__ == "__main__":
    json.dump(run(), sys.stdout, indent=2)
    sys.stdout.write("\n")
