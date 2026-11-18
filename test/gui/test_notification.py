from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.gui.Notification import Notification


class TestNotification(TestCase):
    @patch("blueman.gui.Notification._NotificationBubble")
    @patch("blueman.gui.Notification._NotificationDialog")
    @patch("blueman.gui.Notification.Gio.bus_get_sync")
    @patch("blueman.gui.Notification.Gio.Settings")
    def test_force_dialog_with_capable_notification_daemon(
        self,
        settings: MagicMock,
        bus_get_sync: MagicMock,
        dialog: MagicMock,
        bubble: MagicMock,
    ) -> None:
        settings.return_value.__getitem__.return_value = True
        bus_get_sync.return_value.call_sync.return_value.unpack.return_value = (["body", "actions"],)
        actions = [("confirm", "Confirm")]

        notification = Notification("Summary", "Message", actions=actions, force_dialog=True)

        dialog.assert_called_once_with("Summary", "Message", -1, False, actions, None, None, None)
        bubble.assert_not_called()
        self.assertIs(notification, dialog.return_value)

    @patch("blueman.gui.Notification._NotificationBubble")
    @patch("blueman.gui.Notification._NotificationDialog")
    @patch("blueman.gui.Notification.Gio.bus_get_sync")
    @patch("blueman.gui.Notification.Gio.Settings")
    def test_uses_bubble_by_default_with_capable_notification_daemon(
        self,
        settings: MagicMock,
        bus_get_sync: MagicMock,
        dialog: MagicMock,
        bubble: MagicMock,
    ) -> None:
        settings.return_value.__getitem__.return_value = True
        bus_get_sync.return_value.call_sync.return_value.unpack.return_value = (["body", "actions"],)
        actions = [("confirm", "Confirm")]

        notification = Notification("Summary", "Message", actions=actions)

        bubble.assert_called_once_with("Summary", "Message", -1, False, actions, None, None, None)
        dialog.assert_not_called()
        self.assertIs(notification, bubble.return_value)
