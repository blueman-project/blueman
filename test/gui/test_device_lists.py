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

from blueman.gui.GenericList import GenericList
from blueman.gui.DeviceList import DeviceList
from blueman.gui.DeviceSelectorList import DeviceSelectorList


class FakeDevice:
    def __init__(self) -> None:
        self.item_reads: list[str] = []
        self.getall_reads = 0
        self.properties = {
            "Adapter": "/org/bluez/hci0",
            "Address": "AA:BB:CC:DD:EE:FF",
            "Alias": " Keyboard ",
            "Icon": "input-keyboard",
            "Paired": False,
            "Trusted": False,
        }

    def get_properties(self):
        self.getall_reads += 1
        return dict(self.properties)

    def __getitem__(self, key):
        self.item_reads.append(key)
        return self.properties[key]

    def get_object_path(self):
        return "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"


class TestGenericListSet(TestCase):
    def _make_fake(self):
        fake = types.SimpleNamespace()
        fake.liststore = Gtk.ListStore(str, int, bool)
        fake.list_col_order = {"name": 0, "count": 1, "flag": 2}
        return fake

    def test_set_batches_columns_into_one_row_changed(self):
        fake = self._make_fake()
        tree_iter = fake.liststore.append(["a", 1, False])
        emissions = []
        fake.liststore.connect("row-changed", lambda *_args: emissions.append(1))

        GenericList.set(fake, tree_iter, name="b", count=2, flag=True)

        self.assertEqual(len(emissions), 1)
        self.assertEqual(fake.liststore.get_value(tree_iter, 0), "b")
        self.assertEqual(fake.liststore.get_value(tree_iter, 1), 2)
        self.assertTrue(fake.liststore.get_value(tree_iter, 2))

    def test_set_unknown_column_raises_key_error(self):
        fake = self._make_fake()
        tree_iter = fake.liststore.append(["a", 1, False])

        with self.assertRaises(KeyError):
            GenericList.set(fake, tree_iter, bogus=1)


class TestDeviceListAddDevice(TestCase):
    def _make_fake(self):
        fake = types.SimpleNamespace()
        fake.Adapter = Mock()
        fake.Adapter.get_object_path.return_value = "/org/bluez/hci0"
        fake.append = Mock(return_value=object())
        fake.row_setup_event = Mock()
        fake.get_selected_device = Mock(return_value=object())
        fake.selection = Mock()
        return fake

    def test_add_device_does_a_single_get_all(self):
        fake = self._make_fake()
        device = FakeDevice()

        with patch("blueman.gui.DeviceList.Device", return_value=device):
            DeviceList.add_device(fake, "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF")

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 1)
        self.assertTrue(fake.append.call_args.kwargs["no_name"])
        fake.row_setup_event.assert_called_once()
        tree_iter, dev_arg, properties = fake.row_setup_event.call_args.args
        self.assertIs(dev_arg, device)
        self.assertEqual(properties["Address"], "AA:BB:CC:DD:EE:FF")

    def test_add_device_detects_named_device(self):
        fake = self._make_fake()
        device = FakeDevice()
        device.properties["Name"] = "Keyboard"

        with patch("blueman.gui.DeviceList.Device", return_value=device):
            DeviceList.add_device(fake, "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF")

        self.assertFalse(fake.append.call_args.kwargs["no_name"])

    def test_add_device_skips_foreign_adapter_without_extra_reads(self):
        fake = self._make_fake()
        device = FakeDevice()
        device.properties["Adapter"] = "/org/bluez/hci1"

        with patch("blueman.gui.DeviceList.Device", return_value=device):
            DeviceList.add_device(fake, "/org/bluez/hci1/dev_AA_BB_CC_DD_EE_FF")

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 1)
        fake.append.assert_not_called()
        fake.row_setup_event.assert_not_called()


class TestDeviceSelectorListRowSetup(TestCase):
    def test_row_setup_uses_get_all_properties(self):
        fake = types.SimpleNamespace()
        updates = []
        fake.row_update_event = lambda tree_iter, key, value: updates.append((key, value))
        device = FakeDevice()
        tree_iter = object()

        DeviceSelectorList.row_setup_event(fake, tree_iter, device)

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 1)
        self.assertEqual(updates, [
            ("Trusted", False),
            ("Paired", False),
            ("Alias", "Keyboard"),
            ("Icon", "input-keyboard"),
        ])

    def test_row_setup_reuses_provided_properties(self):
        fake = types.SimpleNamespace()
        fake.row_update_event = lambda tree_iter, key, value: None
        device = FakeDevice()

        DeviceSelectorList.row_setup_event(fake, object(), device, device.get_properties())

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 1)
