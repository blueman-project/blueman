from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.plugins.applet.TransferService import TransferService


def _make_plugin(configured_share_path: str) -> TransferService:
    plugin = TransferService.__new__(TransferService)
    config = MagicMock()
    config.__getitem__.side_effect = lambda key: {"shared-path": configured_share_path}[key]
    plugin._config = config
    return plugin


@patch("blueman.plugins.applet.TransferService.Manager")
@patch("blueman.plugins.applet.TransferService.Notification")
@patch("blueman.plugins.applet.TransferService.Gio.Settings")
class TestSharePathEscaping(TestCase):
    def _body(self, settings_mock: MagicMock, notification_mock: MagicMock, configured: str) -> str:
        plugin = _make_plugin(configured)
        settings_mock.return_value = plugin._config
        with patch.object(TransferService, "_make_share_path", return_value=(Path("/srv/Downloads"), True)):
            plugin.on_load()
        notification_mock.assert_called_once()
        return notification_mock.call_args.args[1]

    def test_escapes_angle_brackets(self, settings_mock: MagicMock, notification_mock: MagicMock,
                                    _manager_mock: MagicMock) -> None:
        body = self._body(settings_mock, notification_mock, "/home/<b>evil</b>")
        self.assertNotIn("<b>evil</b>", body)
        self.assertIn("&lt;b&gt;evil&lt;/b&gt;", body)

    def test_escapes_ampersand(self, settings_mock: MagicMock, notification_mock: MagicMock,
                               _manager_mock: MagicMock) -> None:
        body = self._body(settings_mock, notification_mock, "/home/a & b")
        self.assertIn("&amp;", body)

    def test_escapes_quotes(self, settings_mock: MagicMock, notification_mock: MagicMock,
                            _manager_mock: MagicMock) -> None:
        body = self._body(settings_mock, notification_mock, '/home/"quoted"')
        self.assertNotIn('"quoted"', body)
        self.assertIn("&quot;quoted&quot;", body)


@patch("blueman.plugins.applet.TransferService.Manager")
@patch("blueman.plugins.applet.TransferService.Notification")
@patch("blueman.plugins.applet.TransferService.Gio.Settings")
class TestResetActionTranslated(TestCase):
    def test_reset_label_routed_through_gettext(self, settings_mock: MagicMock, notification_mock: MagicMock,
                                                _manager_mock: MagicMock) -> None:
        plugin = _make_plugin("/does/not/matter")
        settings_mock.return_value = plugin._config
        with patch.object(TransferService, "_make_share_path", return_value=(Path("/srv/Downloads"), True)), \
                patch("blueman.plugins.applet.TransferService._", lambda s: f"<tr>{s}"):
            plugin.on_load()
        actions = notification_mock.call_args.kwargs["actions"]
        self.assertEqual(actions, [("reset", "<tr>Reset to default")])
