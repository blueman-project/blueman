from unittest import TestCase


class TestImports(TestCase):
    def test_GtkStatusIcon_import(self):
        __import__("blueman.main.indicators.GtkStatusIcon")
