import os.path
import pkgutil
from unittest import TestCase, TestSuite


class TestImports(TestCase):
    def __init__(self, mod_name, import_error):
        name = f"test_{mod_name.replace('.', '_')}_import"

        def run():
            try:
                __import__(mod_name)
            except ImportError as e:
                self.assertIsNotNone(import_error)
                self.assertEqual(e.msg, import_error)

        setattr(self, name, run)
        super().__init__(name)


def load_tests(*_args):
    expected_exceptions = {
        "blueman.main.NetworkManager": "NM python bindings not found.",
        "blueman.main.PulseAudioUtils": "Could not load pulseaudio shared library",
    }

    test_cases = TestSuite()
    home, subpath = os.path.dirname(__file__).rsplit("/test/", 1)
    for package in pkgutil.iter_modules([f"{home}/blueman/{subpath}"], f"blueman.{subpath.replace('/', '.')}."):
        test_cases.addTest(TestImports(package.name, expected_exceptions.get(package.name)))

    assert test_cases.countTestCases() > 0

    return test_cases
