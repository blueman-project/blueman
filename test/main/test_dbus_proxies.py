from unittest import TestCase

from blueman.main.DBusProxies import ProxyBase
from blueman.gobject import SingletonGObjectMeta


class TestDBusProxies(TestCase):
    def test_metaclass(self):
        self.assertIsInstance(ProxyBase, SingletonGObjectMeta)
