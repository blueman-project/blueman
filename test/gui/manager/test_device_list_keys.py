from unittest import TestCase
from unittest.mock import Mock, patch

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk

from blueman.gui.manager.ManagerDeviceList import ManagerDeviceList


class FakeDeviceList:
    """Minimal stand-in for ManagerDeviceList.

    Exercises the real, unmodified `_on_key_pressed`/`_toggle_connection`
    methods against a fake selection so the test does not need a live
    Gtk.TreeView, D-Bus connection, or Bluetooth adapter.
    """

    _on_key_pressed = ManagerDeviceList._on_key_pressed
    _toggle_connection = ManagerDeviceList._toggle_connection

    def __init__(self, selected_iter=None, row=None):
        self.menu = Mock()
        self._selected_iter = selected_iter
        self._row = row

    def selected(self):
        return self._selected_iter

    def get(self, _tree_iter, *_cols):
        return self._row


def _event(keyval, state=Gdk.ModifierType(0)):
    return Mock(keyval=keyval, state=state)


class TestDeviceListEnterKey(TestCase):
    def test_enter_connects_disconnected_powered_device(self):
        device = {"UUIDs": [], "Adapter": "/org/bluez/hci0"}
        lst = FakeDeviceList(selected_iter=object(), row={"device": device, "connected": False})
        lst.menu.show_generic_connect_calc.return_value = True

        with patch("blueman.gui.manager.ManagerDeviceList.Adapter") as fake_adapter:
            fake_adapter.return_value.__getitem__ = Mock(return_value=True)  # Powered
            handled = lst._on_key_pressed(None, _event(Gdk.KEY_Return))

        self.assertTrue(handled)
        lst.menu.connect_service.assert_called_once_with(device)
        lst.menu.disconnect_service.assert_not_called()

    def test_kp_enter_disconnects_connected_device(self):
        device = {"UUIDs": [], "Adapter": "/org/bluez/hci0"}
        lst = FakeDeviceList(selected_iter=object(), row={"device": device, "connected": True})
        lst.menu.show_generic_connect_calc.return_value = True

        handled = lst._on_key_pressed(None, _event(Gdk.KEY_KP_Enter))

        self.assertTrue(handled)
        lst.menu.disconnect_service.assert_called_once_with(device)
        lst.menu.connect_service.assert_not_called()

    def test_enter_is_noop_when_generic_connect_not_applicable(self):
        device = {"UUIDs": ["deadbeef"], "Adapter": "/org/bluez/hci0"}
        lst = FakeDeviceList(selected_iter=object(), row={"device": device, "connected": False})
        lst.menu.show_generic_connect_calc.return_value = False

        handled = lst._on_key_pressed(None, _event(Gdk.KEY_Return))

        self.assertTrue(handled)
        lst.menu.connect_service.assert_not_called()
        lst.menu.disconnect_service.assert_not_called()

    def test_enter_is_harmless_with_no_selection(self):
        lst = FakeDeviceList(selected_iter=None, row=None)

        handled = lst._on_key_pressed(None, _event(Gdk.KEY_Return))

        self.assertFalse(handled)
        lst.menu.connect_service.assert_not_called()
        lst.menu.disconnect_service.assert_not_called()

    def test_unrelated_keys_are_ignored(self):
        device = {"UUIDs": [], "Adapter": "/org/bluez/hci0"}
        lst = FakeDeviceList(selected_iter=object(), row={"device": device, "connected": False})

        handled = lst._on_key_pressed(None, _event(Gdk.KEY_a))

        self.assertFalse(handled)
        lst.menu.connect_service.assert_not_called()
