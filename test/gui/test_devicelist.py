from pathlib import Path
import sys
import types
from typing import Any
from unittest import TestCase
from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

constants = types.ModuleType("blueman.Constants")
constants.BIN_DIR = Path("/tmp")
constants.BLUETOOTHD_PATH = Path("/tmp/bluetoothd")
constants.ICON_PATH = Path("/tmp")
constants.PIXMAP_PATH = Path("/tmp")
constants.UI_PATH = Path("/tmp")
sys.modules.setdefault("blueman.Constants", constants)

from blueman.gui.DeviceList import DeviceList  # noqa: E402


class FakeDeviceList:
    """Bind the DeviceList methods under test onto a minimal fake self."""

    discover_devices = DeviceList.discover_devices
    stop_discovery = DeviceList.stop_discovery
    update_progress = DeviceList.update_progress
    _remove_discovery_timeout = DeviceList._remove_discovery_timeout
    clear = DeviceList.clear

    def __init__(self, liststore: Gtk.ListStore | None = None) -> None:
        self.discovering = False
        self._discovery_timeout: int | None = None
        self.Adapter = Mock()
        self.liststore = liststore if liststore is not None else Gtk.ListStore(str)
        self.path_to_row: dict[str, object] = {}
        self.emitted: list[tuple[Any, ...]] = []

    def emit(self, *args: Any) -> None:
        self.emitted.append(args)


class TestDiscoveryTimeout(TestCase):
    def test_discover_stores_timeout_source(self) -> None:
        fake = FakeDeviceList()
        with patch("blueman.gui.DeviceList.GLib.timeout_add", return_value=77) as ta:
            fake.discover_devices(60.0)
        ta.assert_called_once()
        self.assertEqual(fake._discovery_timeout, 77)
        self.assertTrue(fake.discovering)

    def test_discover_noop_when_already_discovering(self) -> None:
        fake = FakeDeviceList()
        fake.discovering = True
        with patch("blueman.gui.DeviceList.GLib.timeout_add", return_value=77) as ta:
            fake.discover_devices(60.0)
        ta.assert_not_called()

    def test_discover_noop_without_adapter(self) -> None:
        fake = FakeDeviceList()
        fake.Adapter = None
        with patch("blueman.gui.DeviceList.GLib.timeout_add", return_value=77) as ta:
            fake.discover_devices(60.0)
        ta.assert_not_called()
        self.assertIsNone(fake._discovery_timeout)

    def test_stop_discovery_removes_source(self) -> None:
        fake = FakeDeviceList()
        fake.discovering = True
        fake._discovery_timeout = 77
        with patch("blueman.gui.DeviceList.GLib.source_remove") as sr:
            fake.stop_discovery()
        sr.assert_called_once_with(77)
        self.assertIsNone(fake._discovery_timeout)
        self.assertFalse(fake.discovering)
        fake.Adapter.stop_discovery.assert_called_once_with()

    def test_stop_discovery_without_source_is_noop(self) -> None:
        fake = FakeDeviceList()
        with patch("blueman.gui.DeviceList.GLib.source_remove") as sr:
            fake.stop_discovery()
        sr.assert_not_called()

    def test_update_progress_not_discovering_drops_id(self) -> None:
        fake = FakeDeviceList()
        fake.discovering = False
        fake._discovery_timeout = 77
        self.assertFalse(fake.update_progress(0.1, 60.0))
        self.assertIsNone(fake._discovery_timeout)

    def test_update_progress_completion_stops_without_double_remove(self) -> None:
        fake = FakeDeviceList()
        fake.discovering = True
        fake._discovery_timeout = 77
        setattr(fake, "_DeviceList__discovery_time", 60.0)
        with patch("blueman.gui.DeviceList.GLib.source_remove") as sr:
            result = fake.update_progress(1.0, 60.0)
        self.assertFalse(result)
        self.assertIsNone(fake._discovery_timeout)
        # id was nulled before stop_discovery, so no source_remove on the
        # currently-running source.
        sr.assert_not_called()
        self.assertFalse(fake.discovering)

    def test_update_progress_midway_keeps_running(self) -> None:
        fake = FakeDeviceList()
        fake.discovering = True
        fake._discovery_timeout = 77
        setattr(fake, "_DeviceList__discovery_time", 0.0)
        self.assertTrue(fake.update_progress(1.0, 60.0))
        self.assertEqual(fake._discovery_timeout, 77)
        self.assertTrue(any(e[0] == "discovery-progress" for e in fake.emitted))
