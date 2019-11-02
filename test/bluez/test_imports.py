import os.path
import pkgutil
from unittest import TestCase, TestSuite


class TestImports(TestCase):
    def __init__(self, mod_name):
        name = f"test_{mod_name.replace('.', '_')}_import"
        setattr(self, name, lambda: __import__(mod_name))
        super().__init__(name)


def load_tests(*_args):
    test_cases = TestSuite()
    home, subpath = os.path.dirname(__file__).rsplit("/test/", 1)
    for package in pkgutil.iter_modules([f"{home}/blueman/{subpath}"], f"blueman.{subpath.replace('/', '.')}."):
        test_cases.addTest(TestImports(package.name))

    assert test_cases.countTestCases() > 0

    return test_cases
