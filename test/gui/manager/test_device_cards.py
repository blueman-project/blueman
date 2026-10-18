import unittest
from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk  # noqa: E402

from blueman.gui.manager.ManagerDeviceCards import (
    DeviceCardSnapshot,
    DeviceCardAction,
    DeviceGroup,
    group_for_state,
    illustration_icon_name,
)


class FakeDevice:
    def __init__(self, object_path: str, name: str, connected: bool, paired: bool) -> None:
        self.object_path = object_path
        self.display_name = name
        self.properties = {
            "Address": "00:11:22:33:44:55",
            "Icon": "bluetooth",
            "Connected": connected,
            "Paired": paired,
        }

    def __getitem__(self, key: str):
        return self.properties[key]

    def get_object_path(self) -> str:
        return self.object_path


class FakeDeviceList(GObject.Object):
    __gsignals__ = {
        "device-property-changed": (GObject.SignalFlags.RUN_LAST, None, (object, object, object)),
        "device-selected": (GObject.SignalFlags.RUN_LAST, None, (object, object)),
    }

    COLUMNS = {
        "device": 0, "alias": 1, "connected": 2, "paired": 3, "trusted": 4, "objpush": 5
    }

    def __init__(self) -> None:
        super().__init__()
        self.liststore = Gtk.ListStore(object, str, bool, bool, bool, bool)
        self.filter = self.liststore.filter_new()
        self.treeview = Gtk.TreeView(model=self.filter)
        self.selection = self.treeview.get_selection()
        self.batteries: dict[str, float] = {}
        self.get_calls = 0

    def add(self, device: FakeDevice) -> Gtk.TreeIter:
        return self.liststore.append([
            device,
            device.display_name,
            device["Connected"],
            device["Paired"],
            False,
            True,
        ])

    def get(self, tree_iter: Gtk.TreeIter, *keys: str) -> dict[str, object]:
        self.get_calls += 1
        return {key: self.liststore.get_value(tree_iter, self.COLUMNS[key]) for key in keys}

    @staticmethod
    def get_device_class(_device: FakeDevice) -> str:
        return "Headphones"

    def get_battery_percentage(self, object_path: str) -> float | None:
        return self.batteries.get(object_path)

    def find_device_by_path(self, object_path: str) -> Gtk.TreeIter | None:
        tree_iter = self.liststore.get_iter_first()
        while tree_iter is not None:
            device = self.liststore.get_value(tree_iter, self.COLUMNS["device"])
            if device.get_object_path() == object_path:
                return tree_iter
            tree_iter = self.liststore.iter_next(tree_iter)
        return None

    def selected(self) -> Gtk.TreeIter | None:
        model, tree_iter = self.selection.get_selected()
        return model.convert_iter_to_child_iter(tree_iter) if tree_iter is not None else None

    def get_selected_device(self) -> FakeDevice | None:
        tree_iter = self.selected()
        return self.get(tree_iter, "device")["device"] if tree_iter is not None else None


class TestDeviceCardSnapshot(unittest.TestCase):
    def test_audio_categories_use_bundled_illustrations(self) -> None:
        self.assertEqual(
            illustration_icon_name("Loudspeaker", "audio-card"),
            "blueman-next-speaker",
        )
        self.assertEqual(
            illustration_icon_name("Headset", "audio-headset"),
            "blueman-next-headphones",
        )
        self.assertEqual(
            illustration_icon_name("Keyboard", "input-keyboard"),
            "input-keyboard",
        )

    def test_groups_are_mutually_exclusive(self) -> None:
        self.assertEqual(group_for_state(connected=True, paired=True), DeviceGroup.CONNECTED)
        self.assertEqual(group_for_state(connected=False, paired=True), DeviceGroup.PAIRED)
        self.assertEqual(group_for_state(connected=False, paired=False), DeviceGroup.AVAILABLE)

    def test_zero_percent_battery_is_available_data(self) -> None:
        snapshot = DeviceCardSnapshot(
            object_path="/org/bluez/hci0/dev_00_00_00_00_00_00",
            name="Keyboard",
            category="Keyboard",
            address="00:00:00:00:00:00",
            icon_name="input-keyboard",
            connected=True,
            paired=True,
            trusted=False,
            can_send=True,
            battery_percentage=0,
        )

        self.assertEqual(snapshot.battery_label, "0%")

    def test_unknown_battery_is_omitted(self) -> None:
        snapshot = DeviceCardSnapshot(
            object_path="/org/bluez/hci0/dev_00_00_00_00_00_00",
            name="Headphones",
            category="Headphones",
            address="00:00:00:00:00:00",
            icon_name="audio-headphones",
            connected=False,
            paired=True,
            trusted=True,
            can_send=False,
            battery_percentage=None,
        )

        self.assertIsNone(snapshot.battery_label)

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_discovery_radar_stops_when_unmapped(self) -> None:
        from blueman.gui.manager.ManagerDeviceCards import DiscoveryRadar

        window = Gtk.Window()
        radar = DiscoveryRadar()
        window.add(radar)
        window.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        radar.set_active(True)
        self.assertGreater(radar._animation_source, 0)
        window.hide()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        self.assertEqual(radar._animation_source, 0)
        window.destroy()

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_discovery_radar_respects_reduced_motion(self) -> None:
        from blueman.gui.manager.ManagerDeviceCards import DiscoveryRadar

        window = Gtk.Window()
        radar = DiscoveryRadar()
        window.add(radar)
        window.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        theme = Mock()
        theme.reduced_motion.return_value = True
        with patch("blueman.gui.theme.ThemeManager.ThemeManager.get_default", return_value=theme):
            radar.set_active(True)
        self.assertEqual(radar._animation_source, 0)
        window.destroy()

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_cards_follow_model_structure_and_bridge_selection(self) -> None:
        from blueman.gui.manager.ManagerDeviceCards import ManagerDeviceCards

        device_list = FakeDeviceList()
        connected = FakeDevice("/device/connected", "Headphones", True, True)
        available = FakeDevice("/device/available", "Keyboard", False, False)
        connected_iter = device_list.add(connected)
        available_iter = device_list.add(available)

        cards = ManagerDeviceCards(device_list)
        self.assertTrue(cards.get_hexpand())
        self.assertTrue(all(section.get_hexpand() for section in cards._section_containers.values()))
        self.assertTrue(all(section.get_hexpand() for section in cards._sections.values()))
        self.assertFalse(cards._discovery_revealer.get_reveal_child())
        cards.set_discovery_state(True, 0.42)
        self.assertTrue(cards._discovery_revealer.get_reveal_child())
        self.assertIn("42%", cards._discovery_label.get_text())
        stop_requests: list[bool] = []
        cards.connect("stop-discovery-requested", lambda _cards: stop_requests.append(True))
        cards._stop_discovery.clicked()
        self.assertEqual(stop_requests, [True])
        cards.set_discovery_state(False)
        self.assertEqual(set(cards.cards_by_path), {connected.object_path, available.object_path})
        self.assertEqual(cards.cards_by_path[connected.object_path].snapshot.group, DeviceGroup.CONNECTED)
        self.assertTrue(
            cards.cards_by_path[connected.object_path]._icon.get_style_context().has_class(
                "device-avatar-headphones"
            )
        )
        self.assertFalse(cards._section_containers[DeviceGroup.PAIRED].get_visible())
        self.assertEqual(cards._section_titles[DeviceGroup.CONNECTED].get_text(), "Connected (1)")

        device_list.get_calls = 0
        cards.search_entry.set_text("00:11:22")
        cards._apply_search()
        self.assertTrue(cards.cards_by_path[connected.object_path].get_visible())
        self.assertTrue(cards.cards_by_path[available.object_path].get_visible())
        cards.search_entry.set_text("HEADPHONES")
        cards._apply_search()
        self.assertTrue(cards.cards_by_path[connected.object_path].get_visible())
        self.assertFalse(cards.cards_by_path[available.object_path].get_visible())
        self.assertEqual(device_list.get_calls, 0, "search must not query the backing model or D-Bus")
        cards.search_entry.set_text("")
        cards._apply_search()

        from blueman.gui.manager.ManagerDeviceInspector import ManagerDeviceInspector
        inspector = ManagerDeviceInspector(cards)
        device_list.emit("device-selected", connected, connected_iter)
        self.assertEqual(inspector._name.get_text(), "Headphones")
        self.assertEqual(inspector._address.get_text(), "00:11:22:33:44:55")
        self.assertEqual(inspector._primary._tile_label.get_text(), "Disconnect")
        self.assertEqual(inspector._paired.get_text(), "Yes")
        self.assertEqual(inspector._trusted.get_text(), "No")
        self.assertIs(inspector._primary.get_parent().get_children()[0], inspector._primary)
        device_list.liststore.set_value(connected_iter, device_list.COLUMNS["alias"], "Studio Headphones")
        device_list.emit(
            "device-property-changed", connected, connected_iter, ("Alias", "Studio Headphones")
        )
        self.assertEqual(inspector._name.get_text(), "Studio Headphones")
        inspector_requests: list[tuple[str, str]] = []
        inspector.connect(
            "action-requested",
            lambda _inspector, path, action, _anchor: inspector_requests.append((path, action)),
        )
        inspector._primary.clicked()
        self.assertEqual(inspector_requests, [(connected.object_path, DeviceCardAction.DISCONNECT.value)])

        connected_card = cards.cards_by_path[connected.object_path]
        device_list.liststore.set_value(
            connected_iter, device_list.COLUMNS["alias"], "Office Headphones"
        )
        device_list.emit(
            "device-property-changed", connected, connected_iter, ("Alias", "Office Headphones")
        )
        self.assertIs(cards.cards_by_path[connected.object_path], connected_card)
        self.assertEqual(connected_card.snapshot.name, "Office Headphones")

        available_card = cards.cards_by_path[available.object_path]
        requested: list[tuple[str, str]] = []
        cards.connect(
            "action-requested",
            lambda _cards, path, action, _anchor: requested.append((path, action)),
        )
        valid, connected_filter_iter = device_list.filter.convert_child_iter_to_iter(connected_iter)
        self.assertTrue(valid)
        device_list.selection.select_iter(connected_filter_iter)
        available_card._primary_action.clicked()
        self.assertEqual(
            requested,
            [(available.object_path, DeviceCardAction.PAIR.value)],
        )
        self.assertEqual(device_list.get_selected_device(), available)

        cards._sections[DeviceGroup.AVAILABLE].select_row(available_card)
        self.assertEqual(device_list.get_selected_device(), available)

        device_list.liststore.remove(available_iter)
        available_card._more_action.clicked()
        self.assertEqual(len(requested), 1, "a removed card must not dispatch an action")
        cards.sync_structure()
        self.assertNotIn(available.object_path, cards.cards_by_path)
        cards.destroy()
        inspector.destroy()


if __name__ == "__main__":
    unittest.main()
