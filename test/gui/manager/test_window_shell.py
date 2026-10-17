import unittest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from blueman.gui.manager.ManagerWindow import (
    COMPACT_SIDEBAR_BREAKPOINT,
    navigation_items,
    should_compact_sidebar,
)


class TestManagerWindowShell(unittest.TestCase):
    def test_sidebar_compacts_only_below_breakpoint(self) -> None:
        self.assertTrue(should_compact_sidebar(COMPACT_SIDEBAR_BREAKPOINT - 1))
        self.assertFalse(should_compact_sidebar(COMPACT_SIDEBAR_BREAKPOINT))

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


if __name__ == "__main__":
    unittest.main()
