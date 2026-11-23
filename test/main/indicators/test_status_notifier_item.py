from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.main.indicators.StatusNotifierItem import MenuService
from blueman.plugins.applet.Menu import MenuItemDict


def _make_item(item_id: int, text: str) -> MenuItemDict:
    return {
        "id": item_id,
        "text": text,
        "icon_name": "blueman",
        "markup": False,
        "sensitive": True,
    }


class TestMenuService(TestCase):
    def _create_service(self) -> MenuService:
        with patch("blueman.main.DbusService.Gio.bus_get_sync"):
            return MenuService(MagicMock())

    def test_set_items_skips_identical_updates(self) -> None:
        svc = self._create_service()
        item = _make_item(0, "Devices...")

        with patch("blueman.main.indicators.StatusNotifierItem.GLib.timeout_add", return_value=42) as timeout_add, \
             patch.object(svc, "emit_signal") as emit_signal:
            svc.set_items([item])
            self.assertEqual(svc._revision, 1)
            timeout_add.assert_called_once_with(100, svc._advertise_revision)

            # Identical update while debounce timer is pending is a no-op
            svc.set_items([_make_item(0, "Devices...")])
            self.assertEqual(svc._revision, 1)
            timeout_add.assert_called_once()

            # Timer fires once and stops
            self.assertFalse(svc._advertise_revision())
            emit_signal.assert_called_once_with("LayoutUpdated", 1, 0)

            # Identical update after advertisement is also a no-op
            layout_before = svc._get_layout(0, -1, [])
            svc.set_items([_make_item(0, "Devices...")])
            self.assertEqual(svc._revision, 1)
            self.assertIs(svc._get_layout(0, -1, []), layout_before)
            timeout_add.assert_called_once()

            # Changed item bumps revision, invalidates cache, and schedules debounce
            svc.set_items([_make_item(0, "Adapters...")])
            self.assertEqual(svc._revision, 2)
            self.assertIsNone(svc._layout_cache)
            self.assertEqual(timeout_add.call_count, 2)

    def test_initial_empty_set_items_still_advertises(self) -> None:
        svc = self._create_service()
        with patch("blueman.main.indicators.StatusNotifierItem.GLib.timeout_add", return_value=7) as timeout_add:
            svc.set_items([])
            self.assertEqual(svc._revision, 1)
            timeout_add.assert_called_once_with(100, svc._advertise_revision)

    def test_unregister_cancels_timer_and_clears_cache(self) -> None:
        svc = self._create_service()
        with patch("blueman.main.indicators.StatusNotifierItem.GLib.timeout_add", return_value=99), \
             patch("blueman.main.indicators.StatusNotifierItem.GLib.source_remove") as source_remove:
            svc.set_items([_make_item(0, "Devices...")])
            svc._get_layout(0, -1, [])
            self.assertIsNotNone(svc._layout_cache)

            svc.unregister()
            source_remove.assert_called_once_with(99)
            self.assertIsNone(svc._source_id)
            self.assertIsNone(svc._layout_cache)
