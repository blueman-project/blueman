from unittest import TestCase


class TestImports(TestCase):
    def test_import(self):
        __import__("_blueman")
