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
            [None, "app.inquiry", "app.preferences", "app.services", "app.plugins"],
        )

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_shell_wraps_existing_content_without_replacing_it(self) -> None:
        from blueman.gui.manager.ManagerWindow import ManagerWindowShell

        window = Gtk.Window()
        content = Gtk.Grid(visible=True)
        window.add(content)

        shell = ManagerWindowShell(window, content, "Blueman Next")

        self.assertIs(window.get_child(), shell.main_paned)
        self.assertIs(content.get_parent(), shell.main_paned)
        window.destroy()


if __name__ == "__main__":
    unittest.main()
