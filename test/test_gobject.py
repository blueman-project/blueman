from unittest import TestCase

from gi.repository.GObject import GObject

from blueman.gobject import SingletonGObjectMeta


class TestGObjectMeta(TestCase):
    class A(GObject, metaclass=SingletonGObjectMeta):
        pass

    class B(GObject, metaclass=SingletonGObjectMeta):
        pass

    def test_instantiation(self):
        self.assertIsInstance(self.A(), GObject)

    def test_singleton(self):
        self.assertEqual(self.A(), self.A())

    def test_separation(self):
        self.assertNotEqual(self.A(), self.B())
