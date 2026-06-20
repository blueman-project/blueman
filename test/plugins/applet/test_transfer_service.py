import tempfile
from datetime import datetime
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.plugins.applet.TransferService import Agent, TransferService, reserve_destination


def _make_agent(resolve_device: object = None) -> Agent:
    agent = Agent.__new__(Agent)
    agent._allowed_devices = set()
    agent._notification = None
    agent._pending_transfers = {}
    agent.transfers = {}
    config = MagicMock()
    config.__getitem__.side_effect = lambda key: True if key == "opp-accept" else ""
    agent._config = config
    agent._resolve_device = resolve_device or (lambda source, address: ("Phone", True))
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
        agent._allowed_devices.add("11:22:33:44:55:66")  # a later, overlapping request's address
        remove_cb()
        self.assertNotIn("AA:BB:CC:DD:EE:FF", agent._allowed_devices)
        self.assertIn("11:22:33:44:55:66", agent._allowed_devices)


@patch("blueman.plugins.applet.TransferService.GLib")
@patch("blueman.plugins.applet.TransferService.Notification")
@patch("blueman.plugins.applet.TransferService.Session")
@patch("blueman.plugins.applet.TransferService.Transfer")
class TestOverlappingPending(TestCase):
    def _setup_two_untrusted(self, agent: Agent, transfer_mock: MagicMock, session_mock: MagicMock) -> None:
        agent._resolve_device = lambda source, address: ("Phone", False)

        def make_transfer(obj_path: str) -> MagicMock:
            transfer = MagicMock()
            transfer.session = "/s" + obj_path
            transfer.name = "first.bin" if obj_path == "/t1" else "second.bin"
            transfer.size = 10
            return transfer

        def make_session(obj_path: str) -> MagicMock:
            session = MagicMock()
            session.root = "/root"
            session.address = "AA:AA" if obj_path == "/s/t1" else "BB:BB"
            session.source = "/org/bluez/hci0"
            return session

        transfer_mock.side_effect = make_transfer
        session_mock.side_effect = make_session

    def test_overlapping_requests_keep_independent_records(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                                           notification_mock: MagicMock, _glib_mock: MagicMock) -> None:
        agent = _make_agent()
        self._setup_two_untrusted(agent, transfer_mock, session_mock)
        ok_a, err_a, ok_b, err_b = MagicMock(), MagicMock(), MagicMock(), MagicMock()

        agent._authorize_push("/t1", ok_a, err_a)
        agent._authorize_push("/t2", ok_b, err_b)
        self.assertEqual(set(agent._pending_transfers), {"/t1", "/t2"})

        on_action_a = notification_mock.call_args_list[0].kwargs["actions_cb"]
        on_action_b = notification_mock.call_args_list[1].kwargs["actions_cb"]

        on_action_a("accept")
        self.assertEqual(agent.transfers["/t1"]["path"].name, "first.bin")
        ok_a.assert_called_once()
        self.assertNotIn("/t1", agent._pending_transfers)
        self.assertIn("/t2", agent._pending_transfers)  # the second request is untouched by the first's action

        on_action_b("reject")
        err_b.assert_called_once()
        self.assertNotIn("/t2", agent._pending_transfers)
        self.assertNotIn("/t2", agent.transfers)


class TestReserveDestination(TestCase):
    _NOW = datetime(2020, 1, 2, 3, 4, 5)
    _STAMP = "20200102030405"

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_no_collision_uses_plain_name(self) -> None:
        dest = reserve_destination(self.dir, "file.bin", self._NOW)
        self.assertEqual(dest, self.dir / "file.bin")
        self.assertTrue(dest.exists())

    def test_first_collision_uses_timestamp(self) -> None:
        (self.dir / "file.bin").write_text("existing")
        dest = reserve_destination(self.dir, "file.bin", self._NOW)
        self.assertEqual(dest, self.dir / f"{self._STAMP}_file.bin")

    def test_second_collision_uses_indexed_timestamp(self) -> None:
        (self.dir / "file.bin").write_text("existing")
        (self.dir / f"{self._STAMP}_file.bin").write_text("existing")
        dest = reserve_destination(self.dir, "file.bin", self._NOW)
        self.assertEqual(dest, self.dir / f"{self._STAMP}_1_file.bin")

    def test_same_second_calls_never_collide(self) -> None:
        # Two transfers of the same name completing in the same second must each
        # reserve a distinct, freshly-created destination — no overwrite.
        reserved = [reserve_destination(self.dir, "photo.jpg", self._NOW) for _ in range(5)]
        self.assertEqual(len(set(reserved)), 5)
        for dest in reserved:
            self.assertTrue(dest.exists())

    def test_reserved_file_is_exclusive(self) -> None:
        dest = reserve_destination(self.dir, "x", self._NOW)
        # A second reservation must not hand back the same path it just created.
        other = reserve_destination(self.dir, "x", self._NOW)
        self.assertNotEqual(dest, other)

    def test_fuzz_weird_names_stay_unique_and_safe(self) -> None:
        names = ["a b.bin", "résumé.pdf", ".hidden", "name.with.dots.tar.gz",
                 "UPPER.TXT", "  spaces  ", "emoji-😀.png", "a" * 200 + ".bin"]
        for raw in names:
            with self.subTest(name=raw):
                first = reserve_destination(self.dir, raw, self._NOW)
                second = reserve_destination(self.dir, raw, self._NOW)
                self.assertNotEqual(first, second)
                self.assertTrue(first.exists() and second.exists())
                # Reserved name must stay within the destination directory.
                self.assertEqual(first.parent, self.dir)
                self.assertEqual(second.parent, self.dir)


class TestDeviceResolverInjection(TestCase):
    def test_plugin_resolver_delegates_to_manager(self) -> None:
        plugin = TransferService.__new__(TransferService)
        plugin.parent = MagicMock()
        device = plugin.parent.Manager.find_device.return_value
        device.display_name = "Watch"
        device.__getitem__.side_effect = lambda key: True if key == "Trusted" else None

        name, trusted = plugin._resolve_device("/org/bluez/hci0", "AA:BB:CC:DD:EE:FF")

        self.assertEqual((name, trusted), ("Watch", True))
        plugin.parent.Manager.get_adapter.assert_called_once_with("/org/bluez/hci0")
        plugin.parent.Manager.find_device.assert_called_once()

    @patch("blueman.plugins.applet.TransferService.GLib")
    @patch("blueman.plugins.applet.TransferService.Notification")
    @patch("blueman.plugins.applet.TransferService.Session")
    @patch("blueman.plugins.applet.TransferService.Transfer")
    def test_agent_uses_injected_resolver(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                          _notification_mock: MagicMock, _glib_mock: MagicMock) -> None:
        resolver = MagicMock(return_value=("Laptop", True))
        agent = _make_agent(resolver)
        _configure_transfer(transfer_mock, session_mock, address="AA:BB:CC:DD:EE:FF")

        agent._authorize_push("/transfer", MagicMock(), MagicMock())

        resolver.assert_called_once_with("/org/bluez/hci0", "AA:BB:CC:DD:EE:FF")
        self.assertFalse(hasattr(agent, "_applet"))

    @patch("blueman.plugins.applet.TransferService.GLib")
    @patch("blueman.plugins.applet.TransferService.Notification")
    @patch("blueman.plugins.applet.TransferService.Session")
    @patch("blueman.plugins.applet.TransferService.Transfer")
    def test_resolver_failure_falls_back_to_address(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                                    notification_mock: MagicMock, _glib_mock: MagicMock) -> None:
        resolver = MagicMock(side_effect=RuntimeError("no device"))
        agent = _make_agent(resolver)
        agent._config.__getitem__.side_effect = lambda key: False  # force the confirmation path
        _configure_transfer(transfer_mock, session_mock, address="AA:BB:CC:DD:EE:FF", size=10)

        agent._authorize_push("/transfer", MagicMock(), MagicMock())

        body = notification_mock.call_args.args[1]
        self.assertIn("AA:BB:CC:DD:EE:FF", body)  # falls back to the raw address as the display name
