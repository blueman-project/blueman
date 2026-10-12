from unittest import TestCase
from unittest.mock import ANY, MagicMock, Mock, patch

from blueman.bluemantyping import ObjectPath
from blueman.main.applet.BluezAgent import BluezAgent


class TestBluezAgent(TestCase):
    @patch("blueman.main.applet.BluezAgent.Notification")
    def test_confirmation_uses_persistent_dialog(self, notification: MagicMock) -> None:
        agent = Mock()
        agent.get_device_string.return_value = "<b>Keyboard</b> (00:11:22:33:44:55)"
        actions = [("confirm", "Confirm"), ("deny", "Deny")]

        BluezAgent._on_request_confirmation(
            agent,
            ObjectPath("/org/bluez/hci0/dev_00_11_22_33_44_55"),
            123456,
            Mock(),
            Mock(),
        )

        notification.assert_called_once_with(
            "Bluetooth",
            "Pairing request for:\n<b>Keyboard</b> (00:11:22:33:44:55)\n"
            "Confirm value for authentication: <b>123456</b>",
            0,
            actions=actions,
            actions_cb=ANY,
            icon_name="blueman",
            force_dialog=True,
        )
        notification.return_value.show.assert_called_once_with()
