import unittest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GObject, Gtk  # noqa: E402

from blueman.gui.manager.ManagerDeviceCards import (
    DeviceCardSnapshot,
    DeviceGroup,
    group_for_state,
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

    COLUMNS = {"device": 0, "alias": 1, "connected": 2, "paired": 3, "trusted": 4}

    def __init__(self) -> None:
        super().__init__()
        self.liststore = Gtk.ListStore(object, str, bool, bool, bool)
        self.filter = self.liststore.filter_new()
        self.treeview = Gtk.TreeView(model=self.filter)
        self.selection = self.treeview.get_selection()
        self.batteries: dict[str, float] = {}

    def add(self, device: FakeDevice) -> Gtk.TreeIter:
        return self.liststore.append([
            device,
            device.display_name,
            device["Connected"],
            device["Paired"],
            False,
        ])

    def get(self, tree_iter: Gtk.TreeIter, *keys: str) -> dict[str, object]:
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
            battery_percentage=None,
        )

        self.assertIsNone(snapshot.battery_label)

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_cards_follow_model_structure_and_bridge_selection(self) -> None:
        from blueman.gui.manager.ManagerDeviceCards import ManagerDeviceCards

        device_list = FakeDeviceList()
        connected = FakeDevice("/device/connected", "Headphones", True, True)
        available = FakeDevice("/device/available", "Keyboard", False, False)
        connected_iter = device_list.add(connected)
        available_iter = device_list.add(available)

        cards = ManagerDeviceCards(device_list)
        self.assertEqual(set(cards.cards_by_path), {connected.object_path, available.object_path})
        self.assertEqual(cards.cards_by_path[connected.object_path].snapshot.group, DeviceGroup.CONNECTED)

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
        cards._sections[DeviceGroup.AVAILABLE].select_row(available_card)
        self.assertEqual(device_list.get_selected_device(), available)

        device_list.liststore.remove(available_iter)
        cards.sync_structure()
        self.assertNotIn(available.object_path, cards.cards_by_path)
        cards.destroy()


if __name__ == "__main__":
    unittest.main()
