from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.plugins.applet.TransferService import Agent, TransferService


def _make_agent() -> Agent:
    agent = Agent.__new__(Agent)
    agent._allowed_devices = set()
    agent._notification = None
    agent._pending_transfer = None
    agent.transfers = {}
    config = MagicMock()
    config.__getitem__.side_effect = lambda key: True if key == "opp-accept" else ""
    agent._config = config
    agent._applet = MagicMock()
    device = agent._applet.Manager.find_device.return_value
    device.display_name = "Phone"
    device.__getitem__.side_effect = lambda key: True if key == "Trusted" else None
    return agent


def _configure_transfer(transfer_mock: MagicMock, session_mock: MagicMock, *, address: str,
                        name: str = "file.bin", size: int = 10) -> None:
    transfer = transfer_mock.return_value
    transfer.session = "/sess"
    transfer.name = name
    transfer.size = size
    session = session_mock.return_value
    session.root = "/root"
    session.address = address
    session.source = "/org/bluez/hci0"


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


@patch("blueman.plugins.applet.TransferService.GLib")
@patch("blueman.plugins.applet.TransferService.Notification")
@patch("blueman.plugins.applet.TransferService.Session")
@patch("blueman.plugins.applet.TransferService.Transfer")
class TestAllowedDeviceRemoval(TestCase):
    def _authorize(self, transfer_mock: MagicMock, session_mock: MagicMock, glib_mock: MagicMock,
                   address: str) -> tuple[Agent, object]:
        agent = _make_agent()
        _configure_transfer(transfer_mock, session_mock, address=address)
        agent._authorize_push("/transfer", MagicMock(), MagicMock())
        remove_cb = glib_mock.timeout_add.call_args.args[1]
        return agent, remove_cb

    def test_address_allowed_then_removed(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                          _notification_mock: MagicMock, glib_mock: MagicMock) -> None:
        agent, remove_cb = self._authorize(transfer_mock, session_mock, glib_mock, "AA:BB:CC:DD:EE:FF")
        self.assertIn("AA:BB:CC:DD:EE:FF", agent._allowed_devices)
        remove_cb()
        self.assertNotIn("AA:BB:CC:DD:EE:FF", agent._allowed_devices)

    def test_removal_is_idempotent(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                   _notification_mock: MagicMock, glib_mock: MagicMock) -> None:
        agent, remove_cb = self._authorize(transfer_mock, session_mock, glib_mock, "AA:BB:CC:DD:EE:FF")
        remove_cb()
        remove_cb()  # must not raise even though the address is already gone

    def test_removes_captured_address_not_current_pending(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                                          _notification_mock: MagicMock, glib_mock: MagicMock) -> None:
        agent, remove_cb = self._authorize(transfer_mock, session_mock, glib_mock, "AA:BB:CC:DD:EE:FF")
        agent._allowed_devices.add("11:22:33:44:55:66")
        agent._pending_transfer = {"address": "11:22:33:44:55:66"}  # a later, overlapping request
        remove_cb()
        self.assertNotIn("AA:BB:CC:DD:EE:FF", agent._allowed_devices)
        self.assertIn("11:22:33:44:55:66", agent._allowed_devices)
