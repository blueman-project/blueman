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
    home = os.path.dirname(os.path.dirname(__file__))
    for package in pkgutil.iter_modules([f"{home}/blueman"], f"blueman."):
        test_cases.addTest(TestImports(package.name))

    assert test_cases.countTestCases() > 0

    return test_cases
