from unittest import TestCase


class TestImports(TestCase):
    def test_AppIndicator_import(self):
        try:
            __import__("blueman.main.indicators.AppIndicator")
        except ValueError as e:
            self.assertEqual(e.args, ("Namespace AppIndicator3 not available",))

    def test_GtkStatusIcon_import(self):
        __import__("blueman.main.indicators.GtkStatusIcon")
