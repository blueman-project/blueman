import unittest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from blueman.gui.manager.DeviceBrands import (
    KNOWN_BRANDS,
    ProductKind,
    brand_for,
    display_category,
    product_kind,
)
from test.gui.manager.test_device_cards import FakeDevice, FakeDeviceList


class TestBrandDetection(unittest.TestCase):
    def test_names_identify_known_brands(self) -> None:
        cases = {
            "Philips TAB8505": "philips",
            "OnePlus Nord Buds 3 Pro": "oneplus",
            "realme Watch 5": "realme",
            "JBL Flip 6": "jbl",
            "WH-1000XM5": "sony",
            "Galaxy Buds2 Pro": "samsung",
            "AirPods Pro": "apple",
            "MX Master 3S": "logitech",
            "Bose QC Earbuds II": "bose",
            "Nothing Ear (2)": "nothing",
            "Redmi Buds 4": "xiaomi",
            "DualSense Wireless Controller": "sony",
        }
        for name, key in cases.items():
            with self.subTest(name=name):
                brand = brand_for(name)
                self.assertIsNotNone(brand)
                assert brand is not None
                self.assertEqual(brand.key, key)

    def test_unrelated_names_are_not_branded(self) -> None:
        for name in ("Car Kit", "Kitchen speaker", "Something Else", "Unnamed device", "Mixer"):
            with self.subTest(name=name):
                self.assertIsNone(brand_for(name))

    def test_manufacturer_id_is_used_only_when_the_name_is_silent(self) -> None:
        brand = brand_for("Wireless Earbuds", [0x004C])
        assert brand is not None
        self.assertEqual(brand.key, "apple")
        name_brand = brand_for("JBL Tune 230NC", [0x004C])
        assert name_brand is not None
        self.assertEqual(name_brand.key, "jbl")
        self.assertIsNone(brand_for("Wireless Earbuds", [0xFFFF]))

    def test_brand_keys_and_classes_are_unique(self) -> None:
        keys = [brand.key for brand in KNOWN_BRANDS]
        self.assertEqual(len(keys), len(set(keys)))

    def test_product_kind_only_replaces_uninformative_classes(self) -> None:
        self.assertEqual(product_kind("realme Watch 5"), ProductKind.WATCH)
        self.assertEqual(product_kind("OnePlus Nord Buds 3 Pro"), ProductKind.EARBUDS)
        self.assertEqual(product_kind("Galaxy Watch6"), ProductKind.WATCH)
        self.assertEqual(product_kind("Galaxy Buds2 Pro"), ProductKind.EARBUDS)
        self.assertIsNone(product_kind("Watchtower Hub"))
        self.assertIsNone(product_kind("Philips TAB8505"))
        self.assertEqual(display_category("Unknown", ProductKind.WATCH), "Smartwatch")
        self.assertEqual(display_category("Headset", ProductKind.EARBUDS), "Headset")
        self.assertEqual(display_category("Unknown", None), "Unknown")


class TestBrandPresentation(unittest.TestCase):
    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_cards_and_inspector_show_brand_tint_artwork_and_search(self) -> None:
        from blueman.gui.manager.ManagerDeviceCards import ManagerDeviceCards
        from blueman.gui.manager.ManagerDeviceInspector import ManagerDeviceInspector

        class Unknown(FakeDeviceList):
            @staticmethod
            def get_device_class(_device: FakeDevice) -> str:
                return "Unknown"

        device_list = Unknown()
        watch = FakeDevice("/device/watch", "realme Watch 5", False, True)
        plain = FakeDevice("/device/plain", "Car Kit", False, True)
        watch_iter = device_list.add(watch)
        device_list.add(plain)
        cards = ManagerDeviceCards(device_list)
        inspector = ManagerDeviceInspector(cards)

        card = cards.cards_by_path[watch.object_path]
        self.assertEqual(card.snapshot.artwork, "blueman-next-watch")
        self.assertEqual(card._category.get_text(), "realme · Smartwatch")
        self.assertTrue(card._avatar.get_style_context().has_class("brand-realme"))
        plain_card = cards.cards_by_path[plain.object_path]
        self.assertEqual(plain_card._category.get_text(), "Unknown")
        self.assertTrue(plain_card._avatar.get_style_context().has_class("device-avatar-unknown"))

        cards.search_entry.set_text("REALME")
        cards._apply_search()
        self.assertTrue(card.get_visible())
        self.assertFalse(plain_card.get_visible())

        device_list.emit("device-selected", watch, watch_iter)
        self.assertTrue(inspector._brand_row.get_visible())
        self.assertEqual(inspector._brand.get_text(), "realme")
        self.assertTrue(inspector._avatar.get_style_context().has_class("brand-realme"))
        inspector.destroy()
        cards.destroy()


if __name__ == "__main__":
    unittest.main()
