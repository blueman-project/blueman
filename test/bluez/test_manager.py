from unittest import TestCase

from blueman.bluez.Manager import Manager
from blueman.gobject import SingletonGObjectMeta


class TestManager(TestCase):
    def test_metaclass(self):
        self.assertIsInstance(Manager, SingletonGObjectMeta)
