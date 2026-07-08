from pathlib import Path
import random
import sys
import types
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk

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
        self.getall_reads = 0
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
        self.getall_reads += 1
        return dict(self.properties)

    def __getitem__(self, key):
        self.item_reads.append(key)
        return self.properties[key]

    def get_object_path(self):
        return "/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"


class FakeManagerDeviceList:
    Adapter = None

    def __init__(self) -> None:
        # column state as row_setup_event would have cached it
        self.values = {
            "initial_anim": True,
            "device": FakeDevice(),
            "objpush": False,
            "uuids": (),
            "klass": 0,
            "address": "AA:BB:CC:DD:EE:FF",
            "icon_name": "input-keyboard",
            "paired": False,
            "connected": False,
            "trusted": False,
            "blocked": False,
        }
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

    def _monitor_power_levels(self, tree_iter, device, address):
        self.monitor_calls.append((tree_iter, device, address))

    def _check_power_levels(self):
        return False

    def _disable_power_levels(self, tree_iter):
        self.disabled.append(tree_iter)

    def make_display_name(self, display_name, _klass, _address):
        return display_name

    def make_caption(self, display_name, description, address):
        return f"{display_name} {description} {address}"

    _has_objpush = staticmethod(ManagerDeviceList._has_objpush)
    get_device_class = staticmethod(ManagerDeviceList.get_device_class)


class TestManagerDeviceListProperties(TestCase):
    def test_has_objpush_uses_uuid_iterable(self):
        self.assertTrue(ManagerDeviceList._has_objpush(["00001105-0000-1000-8000-00805f9b34fb"]))
        self.assertFalse(ManagerDeviceList._has_objpush(["0000110a-0000-1000-8000-00805f9b34fb"]))

    def test_row_setup_uses_get_all_properties(self):
        fake = FakeManagerDeviceList()
        device = FakeDevice()
        device.properties["Connected"] = True
        device.properties["Class"] = 0x5A020C
        device.properties["Icon"] = "phone"
        tree_iter = object()

        ManagerDeviceList.row_setup_event(fake, tree_iter, device)

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 1)
        self.assertFalse(fake.values["trusted"])
        self.assertFalse(fake.values["paired"])
        self.assertTrue(fake.values["connected"])
        self.assertFalse(fake.values["blocked"])
        self.assertEqual(fake.values["uuids"], ())
        self.assertEqual(fake.values["klass"], 0x5A020C)
        self.assertEqual(fake.values["address"], device.properties["Address"])
        self.assertEqual(fake.values["icon_name"], "phone")
        self.assertEqual(len(fake.monitor_calls), 1)
        self.assertEqual(fake.monitor_calls[0][2], device.properties["Address"])

    def test_row_setup_reuses_provided_properties(self):
        fake = FakeManagerDeviceList()
        device = FakeDevice()
        tree_iter = object()

        ManagerDeviceList.row_setup_event(fake, tree_iter, device, device.get_properties())

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 1)

    def test_row_update_batches_icon_properties(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        tree_iter = object()

        ManagerDeviceList.row_update_event(fake, tree_iter, "Trusted", True)

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 0)
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
        self.assertEqual(device.getall_reads, 0)
        self.assertEqual(fake.disabled, [tree_iter])
        cinfo.deinit.assert_called_once_with()
        self.assertEqual(fake._monitored_devices, {})

    def test_row_update_alias_uses_cached_state(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        tree_iter = object()

        ManagerDeviceList.row_update_event(fake, tree_iter, "Alias", " New Name ")

        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 0)
        self.assertEqual(fake.values["alias"], "New Name")
        self.assertIn("AA:BB:CC:DD:EE:FF", fake.values["caption"])

    def test_row_update_icon_and_class_update_cache(self):
        fake = FakeManagerDeviceList()
        tree_iter = object()

        ManagerDeviceList.row_update_event(fake, tree_iter, "Icon", "phone")
        ManagerDeviceList.row_update_event(fake, tree_iter, "Class", 42)

        self.assertEqual(fake.values["icon_name"], "phone")
        self.assertEqual(fake.values["klass"], 42)

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
            ManagerDeviceList._monitor_power_levels(fake, tree_iter, device, "AA:BB:CC:DD:EE:FF")
            ManagerDeviceList._monitor_power_levels(fake, tree_iter, device, "AA:BB:CC:DD:EE:FF")

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

    def test_check_power_levels_uses_cached_connected_state(self):
        row_ref = Mock()
        row_ref.valid.return_value = True
        cinfo = Mock()
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.values["connected"] = True
        fake.get_iter = Mock(return_value=object())
        fake._update_power_levels = Mock()
        fake._monitored_devices = {"AA:BB:CC:DD:EE:FF": (row_ref, cinfo)}
        fake._power_levels_timer = 12

        keep = ManagerDeviceList._check_power_levels(fake)

        self.assertTrue(keep)
        self.assertEqual(device.item_reads, [])
        self.assertEqual(device.getall_reads, 0)
        fake._update_power_levels.assert_called_once()
        self.assertIs(fake._update_power_levels.call_args.args[1], device)
        self.assertEqual(len(fake._monitored_devices), 1)

    def test_check_power_levels_drops_disconnected_device(self):
        row_ref = Mock()
        row_ref.valid.return_value = True
        cinfo = Mock()
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.values["connected"] = False
        fake.get_iter = Mock(return_value=object())
        fake._update_power_levels = Mock()
        fake._monitored_devices = {"AA:BB:CC:DD:EE:FF": (row_ref, cinfo)}
        fake._power_levels_timer = 12

        keep = ManagerDeviceList._check_power_levels(fake)

        self.assertFalse(keep)
        self.assertEqual(device.item_reads, [])
        cinfo.deinit.assert_called_once_with()
        self.assertEqual(len(fake.disabled), 1)
        self.assertEqual(fake._monitored_devices, {})
        self.assertIsNone(fake._power_levels_timer)


class TestManagerDeviceListEventPaths(TestCase):
    def test_get_device_class_uncategorized_falls_back_to_major(self):
        self.assertEqual(ManagerDeviceList.get_device_class(0x0540), "Keyboard")
        self.assertEqual(ManagerDeviceList.get_device_class(0x0500), "Peripheral")

    def test_search_func_matches_caption(self):
        fake = FakeManagerDeviceList()
        fake.values["caption"] = "My Keyboard AA:BB"
        # search_func returns False on match (Gtk convention)
        self.assertFalse(ManagerDeviceList.search_func(fake, Mock(), 0, "keyboard", object()))
        self.assertTrue(ManagerDeviceList.search_func(fake, Mock(), 0, "mouse", object()))

    def test_on_battery_created_skips_dbus_read_without_debug_logging(self):
        fake = FakeManagerDeviceList()
        fake._batteries = {}
        battery = MagicMock()

        with patch("blueman.gui.manager.ManagerDeviceList.Battery", return_value=battery):
            ManagerDeviceList.on_battery_created(fake, Mock(), "/org/bluez/hci0/dev_X")

        self.assertIn("/org/bluez/hci0/dev_X", fake._batteries)
        battery.__getitem__.assert_not_called()

    def test_on_battery_created_still_reads_percentage_with_debug_logging(self):
        import logging
        fake = FakeManagerDeviceList()
        fake._batteries = {}
        battery = MagicMock()
        root = logging.getLogger()
        old_level = root.level
        root.setLevel(logging.DEBUG)
        try:
            with patch("blueman.gui.manager.ManagerDeviceList.Battery", return_value=battery), \
                    self.assertLogs(level=logging.DEBUG):
                ManagerDeviceList.on_battery_created(fake, Mock(), "/org/bluez/hci0/dev_Y")
        finally:
            root.setLevel(old_level)

        battery.__getitem__.assert_called_once_with("Percentage")

    def test_drag_recv_uses_cached_address(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.get_path_at_pos = Mock(return_value=(Mock(), Mock()))
        fake.get_iter = Mock(return_value=object())
        selection = Mock()
        selection.get_uris.return_value = ["file:///tmp/f"]
        context = Mock()

        with patch("blueman.gui.manager.ManagerDeviceList.launch") as launch:
            ManagerDeviceList.drag_recv(fake, Mock(), context, 1, 2, selection, 0, 123)

        self.assertEqual(device.item_reads, [])
        launch.assert_called_once()
        self.assertIn("--device=AA:BB:CC:DD:EE:FF", launch.call_args.args[0])

    def _make_click_fake(self, connected, powered):
        fake = FakeManagerDeviceList()
        fake.values["connected"] = connected
        fake.values["uuids"] = ("00001124-0000-1000-8000-00805f9b34fb",)  # HID
        fake.get_path_at_pos = Mock(return_value=(Mock(),))
        fake.filter = Mock()
        fake.filter.get_iter.return_value = object()
        fake.filter.convert_iter_to_child_iter.return_value = object()
        fake.menu = Mock()
        fake.menu.show_generic_connect_calc = lambda uuids: True
        fake.Adapter = MagicMock()
        fake.Adapter.__getitem__ = Mock(return_value=powered)
        fake.Blueman = Mock()
        return fake

    def test_double_click_disconnects_connected_device(self):
        fake = self._make_click_fake(connected=True, powered=True)
        device = fake.values["device"]
        event = Mock(type=Gdk.EventType._2BUTTON_PRESS, button=1, x=1.0, y=2.0)

        ManagerDeviceList._on_event_clicked(fake, Mock(), event)

        self.assertEqual(device.item_reads, [])
        fake.menu.disconnect_service.assert_called_once_with(device)
        fake.Adapter.__getitem__.assert_not_called()

    def test_double_click_connects_when_adapter_powered(self):
        fake = self._make_click_fake(connected=False, powered=True)
        device = fake.values["device"]
        event = Mock(type=Gdk.EventType._2BUTTON_PRESS, button=1, x=1.0, y=2.0)

        ManagerDeviceList._on_event_clicked(fake, Mock(), event)

        self.assertEqual(device.item_reads, [])
        fake.Adapter.__getitem__.assert_called_once_with("Powered")
        fake.menu.connect_service.assert_called_once_with(device)

    def test_ctrl_c_copies_cached_address(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.selected = Mock(return_value=object())
        event = Mock(state=Gdk.ModifierType.CONTROL_MASK, keyval=Gdk.KEY_c)

        with patch("blueman.gui.manager.ManagerDeviceList.Gtk") as gtk:
            handled = ManagerDeviceList._on_key_pressed(fake, Mock(), event)

        self.assertTrue(handled)
        self.assertEqual(device.item_reads, [])
        gtk.Clipboard.get.return_value.set_text.assert_called_once_with("AA:BB:CC:DD:EE:FF", -1)

    def test_tooltip_uses_batched_row_read(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.values.update(connected=True, battery=80.0, rssi=50.0, tpl=50.0)
        path, col = Mock(), Mock()
        fake.get_path_at_pos = Mock(return_value=(path, col))
        fake.get_iter = Mock(return_value=object())
        fake.view_columns = {"device_surface": Mock(), "battery_pb": col, "rssi_pb": Mock(), "tpl_pb": Mock()}
        fake.tooltip_row = path
        fake.tooltip_col = col
        tooltip = Mock()

        shown = ManagerDeviceList.tooltip_query(fake, Mock(), 1, 2, False, tooltip)

        self.assertTrue(shown)
        self.assertEqual(device.item_reads, [])
        markup = tooltip.set_markup.call_args.args[0]
        self.assertIn("Battery: 80%", markup)


class TestManagerDeviceListFilter(TestCase):
    def _make_fake(self, no_name, klass, hide_unnamed):
        fake = FakeManagerDeviceList()
        fake.values["no_name"] = no_name
        fake.values["klass"] = klass
        fake.Config = {"hide-unnamed": hide_unnamed}
        return fake

    def test_filter_hides_unnamed_non_input_device(self):
        fake = self._make_fake(no_name=True, klass=0x5A020C, hide_unnamed=True)  # Smartphone
        self.assertFalse(ManagerDeviceList.filter_func(fake, Mock(), object(), None))
        self.assertEqual(fake.values["device"].item_reads, [])

    def test_filter_keeps_unnamed_keyboard_and_combo(self):
        for klass in (0x0540, 0x05C0):  # Keyboard, Combo
            fake = self._make_fake(no_name=True, klass=klass, hide_unnamed=True)
            self.assertTrue(ManagerDeviceList.filter_func(fake, Mock(), object(), None))

    def test_filter_keeps_named_devices_and_respects_config(self):
        fake = self._make_fake(no_name=False, klass=0x5A020C, hide_unnamed=True)
        self.assertTrue(ManagerDeviceList.filter_func(fake, Mock(), object(), None))
        fake = self._make_fake(no_name=True, klass=0x5A020C, hide_unnamed=False)
        self.assertTrue(ManagerDeviceList.filter_func(fake, Mock(), object(), None))


class TestUpdatePowerLevels(TestCase):
    def test_bar_pixbufs_are_cached_per_level(self):
        fake = FakeManagerDeviceList()
        device = fake.values["device"]
        fake.values.update(cell_fader=Mock(), battery=0.0, rssi=0.0, tpl=0.0)
        fake.get_scale_factor = Mock(return_value=1)
        fake._prepare_fader = Mock()
        fake._bar_pixbuf_cache = {}
        fake._batteries = {}
        cinfo = Mock()
        cinfo.failed = True  # rssi/tpl fall back to 100.0
        tree_iter = object()

        with patch("blueman.gui.manager.ManagerDeviceList.GdkPixbuf") as gdkpixbuf:
            ManagerDeviceList._update_power_levels(fake, tree_iter, device, cinfo)
            first_loads = gdkpixbuf.Pixbuf.new_from_file_at_scale.call_count
            # simulate a second device reaching the same levels
            fake.values.update(battery=0.0, rssi=0.0, tpl=0.0)
            ManagerDeviceList._update_power_levels(fake, tree_iter, device, cinfo)
            second_loads = gdkpixbuf.Pixbuf.new_from_file_at_scale.call_count

        self.assertEqual(first_loads, 2)  # rssi + tpl
        self.assertEqual(second_loads, 2)  # served from cache
        self.assertEqual(fake.values["rssi"], 100.0)
        self.assertEqual(fake.values["tpl"], 100.0)
        self.assertIsNotNone(fake.values["rssi_pb"])
        self.assertIsNotNone(fake.values["tpl_pb"])


class TestRowUpdateFuzz(TestCase):
    """Deterministic randomized state-machine run over row_update_event.

    Feeds random property-changed sequences and checks two invariants after
    every event: the cached liststore state matches a reference model, and the
    device proxy is never read (no D-Bus round-trips on the update path).
    """

    KEYBOARD_UUIDS = ("00001105-0000-1000-8000-00805f9b34fb",)

    @staticmethod
    def _uuid16(short):
        return f"0000{short:04x}-0000-1000-8000-00805f9b34fb"

    def test_randomized_updates_keep_cached_state_consistent(self):
        rng = random.Random(20260708)
        fake = FakeManagerDeviceList()
        fake.filter = Mock()
        device = fake.values["device"]
        tree_iter = object()

        model = {
            "trusted": False, "paired": False, "connected": False, "blocked": False,
            "icon_name": "input-keyboard", "klass": 0, "objpush": False,
        }
        icon_keys = ("Blocked", "Connected", "Paired", "Trusted")

        for _ in range(2000):
            key = rng.choice(icon_keys + ("Alias", "UUIDs", "Icon", "Class", "Name"))

            if key in icon_keys:
                value = rng.random() < 0.5
                model[key.lower()] = value
            elif key == "Alias":
                value = rng.choice(["", " ", "Dev ", " <b>&x</b> ", "名前 ", "plain"])
            elif key == "UUIDs":
                shorts = rng.sample(range(0x1101, 0x1120), rng.randint(0, 5))
                value = [self._uuid16(s) for s in shorts]
                model["objpush"] = 0x1105 in shorts
            elif key == "Icon":
                value = rng.choice(["phone", "audio-headset", None])
                model["icon_name"] = value if value is not None else "blueman"
            elif key == "Class":
                value = rng.choice([rng.randrange(0, 0x1000000), None])
                model["klass"] = value if value is not None else 0
            else:  # Name
                value = "Some Name"

            ManagerDeviceList.row_update_event(fake, tree_iter, key, value)

            self.assertEqual(device.item_reads, [], f"D-Bus read after {key}")
            self.assertEqual(device.getall_reads, 0, f"GetAll after {key}")
            for column in ("trusted", "paired", "connected", "blocked", "icon_name", "klass", "objpush"):
                self.assertEqual(fake.values[column], model[column], f"{column} after {key}")
            if key in icon_keys:
                self.assertEqual(
                    fake.icon_args,
                    (model["icon_name"], model["paired"], model["connected"],
                     model["trusted"], model["blocked"]))
            if key == "Alias":
                self.assertEqual(fake.values["alias"], value.strip())

    def test_has_objpush_fuzz(self):
        rng = random.Random(20260708)
        for _ in range(500):
            shorts = rng.sample(range(0x1000, 0x2000), rng.randint(0, 8))
            uuids = [self._uuid16(s) for s in shorts]
            self.assertEqual(ManagerDeviceList._has_objpush(uuids), 0x1105 in shorts)

    def test_make_display_name_fuzz(self):
        rng = random.Random(20260708)
        for _ in range(500):
            address = ":".join(f"{rng.randrange(256):02X}" for _ in range(6))
            alias = rng.choice([address, address.replace(":", "-"), "Headphones", f"dev-{rng.randrange(100)}"])
            result = ManagerDeviceList.make_display_name(alias, 0, address)
            if alias.replace("-", ":") == address:
                self.assertEqual(result, "Unnamed device")
            else:
                self.assertEqual(result, alias)
