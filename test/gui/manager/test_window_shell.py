import unittest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from blueman.gui.manager.ManagerWindow import (
    COMPACT_SIDEBAR_BREAKPOINT,
    INSPECTOR_WIDTH,
    NARROW_INSPECTOR_WIDTH,
    NARROW_LAYOUT_BREAKPOINT,
    NARROW_SIDEBAR_WIDTH,
    SIDEBAR_WIDTH,
    inspector_width_for,
    navigation_items,
    sidebar_width_for,
    should_compact_sidebar,
)


class TestManagerWindowShell(unittest.TestCase):
    def test_sidebar_compacts_only_below_breakpoint(self) -> None:
        self.assertTrue(should_compact_sidebar(COMPACT_SIDEBAR_BREAKPOINT - 1))
        self.assertFalse(should_compact_sidebar(COMPACT_SIDEBAR_BREAKPOINT))

    def test_intermediate_layout_preserves_dashboard_width(self) -> None:
        self.assertEqual(sidebar_width_for(1397), NARROW_SIDEBAR_WIDTH)
        self.assertEqual(inspector_width_for(1397), NARROW_INSPECTOR_WIDTH)
        self.assertEqual(sidebar_width_for(NARROW_LAYOUT_BREAKPOINT), SIDEBAR_WIDTH)
        self.assertEqual(inspector_width_for(NARROW_LAYOUT_BREAKPOINT), INSPECTOR_WIDTH)

    def test_navigation_only_exposes_working_destinations(self) -> None:
        self.assertEqual(
            [item.action for item in navigation_items()],
            [None, "app.inquiry", "app.send", "app.settings"],
        )

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_shell_replaces_legacy_presentation_but_retains_widgets(self) -> None:
        from blueman.gui.manager.ManagerWindow import ManagerWindowShell

        window = Gtk.Window()
        content = Gtk.Grid(visible=True)
        window.add(content)

        shell = ManagerWindowShell(window, content, "Blueman Next")

        self.assertIs(window.get_child(), shell.main_paned)
        self.assertIsNone(content.get_parent())

        legacy = Gtk.ScrolledWindow(visible=True)
        content.attach(legacy, 0, 2, 1, 1)
        cards = Gtk.Box(visible=True)
        cards.search_entry = Gtk.SearchEntry(visible=True)
        cards.cards_by_path = {}
        shell.install_device_cards(cards, legacy)
        self.assertFalse(legacy.get_visible())
        self.assertTrue(shell._card_view.get_visible())
        inspector = Gtk.Box(visible=True)
        shell.install_device_inspector(inspector)
        shell._inspector_toggle.set_active(True)
        self.assertTrue(shell._inspector_revealer.get_reveal_child())
        window.destroy()

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_borderless_chrome_uses_traffic_lights(self) -> None:
        from unittest.mock import patch
        from blueman.gui.manager.ManagerWindow import ManagerWindowShell

        window = Gtk.Window()
        content = Gtk.Grid(visible=True)
        window.add(content)
        shell = ManagerWindowShell(window, content, "Blueman Next")

        self.assertIs(window.get_titlebar(), shell.header)
        self.assertNotIsInstance(shell.header, Gtk.HeaderBar)
        self.assertEqual(list(shell.traffic_light_buttons), ["close", "minimize", "maximize"])
        with patch.object(window, "iconify") as iconify, patch.object(window, "close") as close:
            shell.traffic_light_buttons["minimize"].clicked()
            shell.traffic_light_buttons["close"].clicked()
        iconify.assert_called_once_with()
        close.assert_called_once_with()
        window.destroy()

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_power_card_shows_real_adapter_name_and_radar_state(self) -> None:
        from blueman.gui.manager.ManagerWindow import ManagerWindowShell

        window = Gtk.Window()
        content = Gtk.Grid(visible=True)
        window.add(content)
        shell = ManagerWindowShell(window, content, "Blueman Next")

        shell.set_adapter_name("Dorin's PC")
        self.assertEqual(shell._adapter_name.get_text(), "Dorin's PC")
        shell.set_adapter_name(None)
        self.assertEqual(shell._adapter_name.get_text(), "This computer")

        shell.set_discovery_state(True)
        self.assertTrue(shell.radar.active)
        shell.set_bluetooth_state(False)
        self.assertFalse(shell.radar.active)
        self.assertTrue(shell.radar.get_style_context().has_class("sidebar-radar-off"))
        window.destroy()

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_minimum_width_allows_compact_breakpoints(self) -> None:
        """Side panes must shrink, or the window can never become narrow enough to compact."""
        from blueman.gui.manager.ManagerWindow import ManagerWindowShell

        window = Gtk.Window()
        content = Gtk.Grid(visible=True)
        window.add(content)
        shell = ManagerWindowShell(window, content, "Blueman Next")
        cards = Gtk.Box(visible=True, width_request=500)
        cards.search_entry = Gtk.SearchEntry(visible=True)
        cards.cards_by_path = {}
        shell.install_device_cards(cards, Gtk.ScrolledWindow())
        shell.install_device_inspector(Gtk.Box(visible=True, width_request=INSPECTOR_WIDTH))
        shell._inspector_revealer.set_reveal_child(True)

        minimum = shell.main_paned.get_preferred_width()[0]
        self.assertLess(minimum, COMPACT_SIDEBAR_BREAKPOINT)
        window.destroy()

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_radar_timer_runs_only_while_mapped_and_active(self) -> None:
        from blueman.gui.manager.ManagerWindow import SidebarRadar

        window = Gtk.OffscreenWindow()
        radar = SidebarRadar()
        window.add(radar)
        radar.set_active(True)
        self.assertEqual(radar._animation_source, 0)  # not mapped yet
        window.show_all()
        self.assertNotEqual(radar._animation_source, 0)
        radar.set_active(False)
        self.assertEqual(radar._animation_source, 0)
        radar.set_active(True)
        window.destroy()
        self.assertEqual(radar._animation_source, 0)


if __name__ == "__main__":
    unittest.main()
