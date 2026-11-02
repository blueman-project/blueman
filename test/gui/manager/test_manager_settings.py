import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk  # noqa: E402

from blueman.gui.manager.ManagerSettings import EXPOSED_SETTINGS


class TestManagerSettings(unittest.TestCase):
    def test_every_exposed_option_exists_in_general_schema(self) -> None:
        root = Path(__file__).parents[3]
        document = ET.parse(root / "data" / "org.blueman.gschema.xml")
        schema = document.find(".//schema[@id='org.blueman.general']")
        self.assertIsNotNone(schema)
        assert schema is not None
        schema_keys = {key.attrib["name"] for key in schema.findall("key")}
        self.assertLessEqual(EXPOSED_SETTINGS, schema_keys)

    @unittest.skipUnless(Gtk.init_check()[0], "GTK display is unavailable")
    def test_page_controls_follow_and_write_settings(self) -> None:
        from unittest.mock import Mock
        from blueman.gui.manager.ManagerSettings import ManagerSettingsPage

        backend = Gio.memory_settings_backend_new()
        root = Path(__file__).parents[3]
        source = Gio.SettingsSchemaSource.new_from_directory(
            str(root / "build-local" / "data"), Gio.SettingsSchemaSource.get_default(), False
        )
        schema = source.lookup("org.blueman.general", False)
        if schema is None:
            self.skipTest("compiled schema not available; run ./blueman-next --build-only")
        settings = Gio.Settings.new_full(schema, backend, None)
        application = Mock()
        page = ManagerSettingsPage(application, settings)

        self.assertEqual(set(page.controls) - {"preferences", "services", "plugins", "reset-adapter"}, EXPOSED_SETTINGS)
        theme = page.controls["theme-variant"]
        theme.buttons["dark"].set_active(True)
        self.assertEqual(settings.get_string("theme-variant"), "dark")
        settings.set_string("theme-variant", "light")
        self.assertTrue(theme.buttons["light"].get_active())
        settings.set_boolean("reduced-motion", True)
        self.assertTrue(page.controls["reduced-motion"].get_active())
        page.controls["preferences"].clicked()
        application.activate_action.assert_called_once_with("preferences", None)
        page.destroy()


if __name__ == "__main__":
    unittest.main()
