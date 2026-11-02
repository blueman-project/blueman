from unittest import TestCase
from unittest.mock import Mock, patch

from blueman.main.AdapterReset import AdapterResetError
from blueman.main.DbusService import DbusError
from blueman.plugins.mechanism.AdapterReset import AdapterReset, AdapterResetFailed


class TestAdapterResetPlugin(TestCase):
    def setUp(self) -> None:
        self.parent = Mock()
        self.plugin = AdapterReset(self.parent)

    def test_registers_method(self) -> None:
        self.parent.add_method.assert_called_once_with(
            "ResetAdapter", ("s",), ("s",), self.plugin._reset_adapter, pass_sender=True)

    def test_authorizes_before_resetting(self) -> None:
        with patch("blueman.plugins.mechanism.AdapterReset.reset_controller", return_value="rebind") as reset:
            self.assertEqual(self.plugin._reset_adapter("hci0", ":1.5"), "rebind")
        self.parent.confirm_authorization.assert_called_once_with(":1.5", "org.blueman.adapter.reset")
        reset.assert_called_once_with("hci0")
        self.parent.timer.resume.assert_called_once()

    def test_unauthorized_caller_does_not_reset(self) -> None:
        self.parent.confirm_authorization.side_effect = DbusError("Not authorized")
        with patch("blueman.plugins.mechanism.AdapterReset.reset_controller") as reset:
            with self.assertRaises(DbusError):
                self.plugin._reset_adapter("hci0", ":1.5")
        reset.assert_not_called()

    def test_failure_becomes_dbus_error(self) -> None:
        with patch("blueman.plugins.mechanism.AdapterReset.reset_controller",
                   side_effect=AdapterResetError("hci0 has no device in sysfs")):
            with self.assertRaises(AdapterResetFailed) as raised:
                self.plugin._reset_adapter("hci0", ":1.5")
        self.assertEqual(raised.exception.name, "org.blueman.Error.AdapterResetFailed")
        self.parent.timer.resume.assert_called_once()
