from unittest import TestCase

from blueman.bluez.obex.Manager import Manager
from blueman.gobject import SingletonGObjectMeta


class TestManager(TestCase):
    def test_metaclass(self):
        self.assertIsInstance(Manager, SingletonGObjectMeta)
