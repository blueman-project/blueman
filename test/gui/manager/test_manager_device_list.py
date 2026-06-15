from pathlib import Path
import sys
import types
from unittest import TestCase
from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

constants = types.ModuleType("blueman.Constants")
constants.BIN_DIR = Path("/tmp")
constants.BLUETOOTHD_PATH = Path("/tmp/bluetoothd")
constants.ICON_PATH = Path("/tmp")
constants.PIXMAP_PATH = Path("/tmp")
constants.UI_PATH = Path("/tmp")
sys.modules.setdefault("blueman.Constants", constants)

from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList


class FakeDevice:
    display_name = "Keyboard"

    def __init__(self) -> None:
        self.item_reads: list[str] = []
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
            "UUIDs": [],
        }

    def get_properties(self):
        return dict(self.properties)

    def __getitem__(self, key):
        self.item_reads.append(key)
        return self.properties[key]


class FakeManagerDeviceList:
    Adapter = None

    def __init__(self) -> None:
        self.values = {"initial_anim": True, "device": FakeDevice(), "objpush": False, "uuids": ()}
        self.set_calls: list[dict[str, object]] = []
        self.monitor_calls = []
        self.disabled = []
        self._monitored_devices = {}

    def get(self, _tree_iter, *keys):
        return {key: self.values[key] for key in keys}

    def set(self, _tree_iter, **kwargs):
        self.values.update(kwargs)
        self.set_calls.append(kwargs)

    def _make_device_icon(self, *args):
        self.icon_args = args
        return Mock()

    def _monitor_power_levels(self, tree_iter, device, properties=None):
        self.monitor_calls.append((tree_iter, device, properties))

    def _check_power_levels(self):
        return False

    def _disable_power_levels(self, tree_iter):
        self.disabled.append(tree_iter)

    def make_display_name(self, display_name, _klass, _address):
        return display_name

    def make_caption(self, display_name, description, address):
        return f"{display_name} {description} {address}"

    _has_objpush = staticmethod(ManagerDeviceList._has_objpush)


class TestManagerDeviceListProperties(TestCase):
    def test_has_objpush_uses_uuid_iterable(self):
        self.assertTrue(ManagerDeviceList._has_objpush(["00001105-0000-1000-8000-00805f9b34fb"]))
        self.assertFalse(ManagerDeviceList._has_objpush(["0000110a-0000-1000-8000-00805f9b34fb"]))

    def test_row_setup_uses_get_all_properties(self):
        fake = FakeManagerDeviceList()
        device = FakeDevice()
        device.properties["Connected"] = True
        tree_iter = object()

        ManagerDeviceList.row_setup_event(fake, tree_iter, device)

        self.assertEqual(device.item_reads, [])
        self.assertFalse(fake.values["trusted"])
        self.assertFalse(fake.values["paired"])
        self.assertTrue(fake.values["connected"])
        self.assertFalse(fake.values["blocked"])
        self.assertEqual(fake.values["uuids"], ())
        self.assertEqual(len(fake.monitor_calls), 1)
        self.assertEqual(fake.monitor_calls[0][2]["Address"], device.properties["Address"])

    def test_row_update_batches_icon_properties(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        tree_iter = object()

        ManagerDeviceList.row_update_event(fake, tree_iter, "Trusted", True)

        self.assertEqual(device.item_reads, [])
        self.assertEqual(fake.icon_args, ("input-keyboard", False, False, True, False))
        self.assertTrue(fake.values["trusted"])

    def test_row_update_connected_false_uses_batched_address(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        cinfo = Mock()
        fake._monitored_devices = {device.properties["Address"]: (Mock(), cinfo)}
        tree_iter = object()

        ManagerDeviceList.row_update_event(fake, tree_iter, "Connected", False)

        self.assertEqual(device.item_reads, [])
        self.assertEqual(fake.disabled, [tree_iter])
        cinfo.deinit.assert_called_once_with()
        self.assertEqual(fake._monitored_devices, {})

    def test_row_update_uuids_updates_cached_state(self):
        fake = FakeManagerDeviceList()
        tree_iter = object()
        uuids = ["00001105-0000-1000-8000-00805f9b34fb"]

        ManagerDeviceList.row_update_event(fake, tree_iter, "UUIDs", uuids)

        self.assertEqual(fake.values["uuids"], tuple(uuids))
        self.assertTrue(fake.values["objpush"])

    def test_drag_motion_uses_cached_objpush_state(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.values["objpush"] = True
        fake.filter = Mock()
        fake.filter.convert_path_to_child_path.return_value = Mock()
        fake.selection = Mock()
        fake.selection.path_is_selected.return_value = False
        fake.get_path_at_pos = Mock(return_value=(Mock(), Mock(), Mock(), Mock()))
        fake.get_iter = Mock(return_value=Mock())
        fake.set_cursor = Mock()

        with patch("blueman.gui.manager.ManagerDeviceList.Gdk.drag_status") as drag_status:
            result = ManagerDeviceList.drag_motion(fake, Mock(), Mock(), 1, 2, 3)

        self.assertTrue(result)
        self.assertEqual(device.item_reads, [])
        drag_status.assert_called_once()
        fake.set_cursor.assert_called_once()


class TestManagerDeviceListPowerTimer(TestCase):
    def test_monitor_power_levels_starts_one_timer(self):
        fake = FakeManagerDeviceList()
        fake.Adapter = Mock()
        fake.Adapter.get_object_path.return_value = "/org/bluez/hci0"
        fake.liststore = Gtk.ListStore(str)
        tree_iter = fake.liststore.append(["Keyboard"])
        fake._monitored_devices = {}
        fake._power_levels_timer = None
        fake._update_power_levels = Mock()
        device = FakeDevice()

        with patch("blueman.gui.manager.ManagerDeviceList.adapter_path_to_name", return_value="hci0"), \
                patch("blueman.gui.manager.ManagerDeviceList.conn_info") as conn_info_cls, \
                patch("blueman.gui.manager.ManagerDeviceList.Gtk.TreeRowReference.new", return_value=Mock()), \
                patch("blueman.gui.manager.ManagerDeviceList.GLib.timeout_add", return_value=12) as timeout_add:
            ManagerDeviceList._monitor_power_levels(fake, tree_iter, device, device.get_properties())
            ManagerDeviceList._monitor_power_levels(fake, tree_iter, device, device.get_properties())

        conn_info_cls.assert_called_once_with("AA:BB:CC:DD:EE:FF", "hci0")
        timeout_add.assert_called_once_with(1000, fake._check_power_levels)
        self.assertEqual(fake._power_levels_timer, 12)
        self.assertEqual(len(fake._monitored_devices), 1)

    def test_check_power_levels_stops_when_no_devices_remain(self):
        row_ref = Mock()
        row_ref.valid.return_value = False
        cinfo = Mock()
        fake = FakeManagerDeviceList()
        fake._monitored_devices = {"AA:BB:CC:DD:EE:FF": (row_ref, cinfo)}
        fake._power_levels_timer = 12

        keep = ManagerDeviceList._check_power_levels(fake)

        self.assertFalse(keep)
        cinfo.deinit.assert_called_once_with()
        self.assertEqual(fake._monitored_devices, {})
        self.assertIsNone(fake._power_levels_timer)
