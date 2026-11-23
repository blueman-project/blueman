from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.main.indicators.GtkStatusIcon import GtkStatusIcon


class TestGtkStatusIcon(TestCase):
    def test_set_menu_destroys_previous_menu(self) -> None:
        tray = MagicMock()
        first_menu = MagicMock()
        second_menu = MagicMock()

        with patch("blueman.main.indicators.GtkStatusIcon.Gtk.StatusIcon"), \
             patch("blueman.main.indicators.GtkStatusIcon.build_menu",
                   side_effect=[first_menu, second_menu]):
            indicator = GtkStatusIcon(tray, "blueman")
            indicator.set_menu([])
            first_menu.destroy.assert_not_called()

            indicator.set_menu([])
            first_menu.destroy.assert_called_once_with()
            second_menu.destroy.assert_not_called()
