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


@patch("blueman.plugins.applet.TransferService.Notification")
class TestTransferCompleted(TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        root = Path(self._tmp.name)
        self.dest_dir = root / "Downloads"
        self.dest_dir.mkdir()
        self.src = root / "incoming.bin"
        self.src.write_text("payload")

    def _plugin(self, size: int = 10) -> TransferService:
        plugin = TransferService.__new__(TransferService)
        plugin._agent = MagicMock()
        plugin._agent.transfers = {"/t": {"path": self.src, "size": size, "name": "Phone"}}
        plugin._normal_transfers = 0
        plugin._silent_transfers = 1
        plugin._notification = None
        return plugin

    def test_unauthorized_transfer_ignored(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin()
        plugin._agent.transfers = {}
        plugin._on_transfer_completed(MagicMock(), "/t", True)
        notification_mock.assert_not_called()

    def test_success_moves_file_and_notifies(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin()
        with patch.object(TransferService, "_make_share_path", return_value=(self.dest_dir, False)):
            plugin._on_transfer_completed(MagicMock(), "/t", True)
        self.assertTrue((self.dest_dir / "incoming.bin").exists())
        self.assertFalse(self.src.exists())
        notification_mock.assert_called_once()
        self.assertNotIn("/t", plugin._agent.transfers)

    def test_failed_move_cleans_placeholder_and_decrements(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin(size=10)
        with patch.object(TransferService, "_make_share_path", return_value=(self.dest_dir, False)), \
                patch("blueman.plugins.applet.TransferService.shutil.move", side_effect=OSError("boom")):
            plugin._on_transfer_completed(MagicMock(), "/t", True)
        self.assertEqual(list(self.dest_dir.iterdir()), [])  # reserved placeholder cleaned up
        self.assertEqual(plugin._silent_transfers, 0)
        self.assertNotIn("/t", plugin._agent.transfers)

    def test_failed_move_decrements_normal_for_large_file(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin(size=400000)
        plugin._normal_transfers = 1
        plugin._silent_transfers = 0
        with patch.object(TransferService, "_make_share_path", return_value=(self.dest_dir, False)), \
                patch("blueman.plugins.applet.TransferService.shutil.move", side_effect=PermissionError):
            plugin._on_transfer_completed(MagicMock(), "/t", False)
        self.assertEqual(plugin._normal_transfers, 0)


class TestTransferStarted(TestCase):
    def _plugin(self, size: int) -> TransferService:
        plugin = TransferService.__new__(TransferService)
        plugin._agent = MagicMock()
        plugin._agent.transfers = {"/t": {"path": Path("/x"), "size": size, "name": "Phone"}}
        plugin._normal_transfers = 0
        plugin._silent_transfers = 0
        return plugin

    def test_large_file_counts_as_normal(self) -> None:
        plugin = self._plugin(400000)
        plugin._on_transfer_started(MagicMock(), "/t")
        self.assertEqual((plugin._normal_transfers, plugin._silent_transfers), (1, 0))

    def test_small_file_counts_as_silent(self) -> None:
        plugin = self._plugin(10)
        plugin._on_transfer_started(MagicMock(), "/t")
        self.assertEqual((plugin._normal_transfers, plugin._silent_transfers), (0, 1))

    def test_unauthorized_transfer_ignored(self) -> None:
        plugin = self._plugin(10)
        plugin._agent = None
        plugin._on_transfer_started(MagicMock(), "/t")  # must not raise


@patch("blueman.plugins.applet.TransferService.Notification")
class TestSessionRemoved(TestCase):
    def _plugin(self, silent: int, normal: int) -> TransferService:
        plugin = TransferService.__new__(TransferService)
        plugin._silent_transfers = silent
        plugin._normal_transfers = normal
        plugin._notification = None
        return plugin

    def test_no_silent_transfers_does_nothing(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin(silent=0, normal=0)
        plugin._on_session_removed(MagicMock(), "/sess")
        notification_mock.assert_not_called()

    def test_only_silent_transfers_notifies(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin(silent=2, normal=0)
        with patch.object(TransferService, "_make_share_path", return_value=(Path("/dl"), False)):
            plugin._on_session_removed(MagicMock(), "/sess")
        notification_mock.assert_called_once()

    def test_mixed_transfers_notifies_more_variant(self, notification_mock: MagicMock) -> None:
        plugin = self._plugin(silent=1, normal=1)
        with patch.object(TransferService, "_make_share_path", return_value=(Path("/dl"), False)):
            plugin._on_session_removed(MagicMock(), "/sess")
        notification_mock.assert_called_once()


class TestAgentControl(TestCase):
    def test_cancel_closes_notification_and_raises(self) -> None:
        from blueman.plugins.applet.TransferService import ObexErrorCanceled
        agent = _make_agent()
        agent._notification = MagicMock()
        with self.assertRaises(ObexErrorCanceled):
            agent._cancel()
        agent._notification.close.assert_called_once()

    def test_release_raises(self) -> None:
        agent = _make_agent()
        with self.assertRaises(Exception):
            agent._release()


@patch("blueman.plugins.applet.TransferService.GLib")
class TestMakeSharePath(TestCase):
    def _plugin(self, configured: str) -> TransferService:
        plugin = TransferService.__new__(TransferService)
        config = MagicMock()
        config.__getitem__.side_effect = lambda key: configured
        config.__setitem__ = MagicMock()
        plugin._config = config
        return plugin

    def test_empty_config_uses_download_dir(self, glib_mock: MagicMock) -> None:
        glib_mock.get_user_special_dir.return_value = "/dl"
        plugin = self._plugin("")
        path, error = plugin._make_share_path()
        self.assertEqual(path, Path("/dl"))
        self.assertFalse(error)

    def test_invalid_dir_flags_error(self, glib_mock: MagicMock) -> None:
        glib_mock.get_user_special_dir.return_value = "/dl"
        plugin = self._plugin("/does/not/exist/here")
        path, error = plugin._make_share_path()
        self.assertEqual(path, Path("/dl"))
        self.assertTrue(error)

    def test_valid_dir_used(self, glib_mock: MagicMock) -> None:
        glib_mock.get_user_special_dir.return_value = "/dl"
        with tempfile.TemporaryDirectory() as tmp:
            plugin = self._plugin(tmp)
            path, error = plugin._make_share_path()
            self.assertEqual(path, Path(tmp))
            self.assertFalse(error)


@patch("blueman.plugins.applet.TransferService.GLib")
@patch("blueman.plugins.applet.TransferService.Notification")
@patch("blueman.plugins.applet.TransferService.Session")
@patch("blueman.plugins.applet.TransferService.Transfer")
class TestAutoAccept(TestCase):
    def test_trusted_large_file_auto_accepts_with_notification(self, transfer_mock: MagicMock, session_mock: MagicMock,
                                                               notification_mock: MagicMock,
                                                               _glib_mock: MagicMock) -> None:
        agent = _make_agent()  # default resolver -> trusted
        _configure_transfer(transfer_mock, session_mock, address="AA:BB:CC:DD:EE:FF", size=400001)
        ok = MagicMock()
        agent._authorize_push("/t", ok, MagicMock())
        ok.assert_called_once()
        self.assertIn("/t", agent.transfers)
        self.assertIn("AA:BB:CC:DD:EE:FF", agent._allowed_devices)
        notification_mock.assert_called_once()


class TestRegisterAgent(TestCase):
    @patch("blueman.plugins.applet.TransferService.Agent")
    def test_register_then_unregister(self, agent_cls: MagicMock) -> None:
        plugin = TransferService.__new__(TransferService)
        plugin._agent = None
        plugin._register_agent()
        agent_cls.assert_called_once_with(plugin._resolve_device)
        agent_cls.return_value.register_at_manager.assert_called_once()
        agent = plugin._agent
        plugin._unregister_agent()
        agent.unregister_from_manager.assert_called_once()
        agent.unregister.assert_called_once()
        self.assertIsNone(plugin._agent)


@patch("blueman.plugins.applet.TransferService.launch")
@patch("blueman.plugins.applet.TransferService.Notification")
class TestOpenAction(TestCase):
    def test_open_action_launches_xdg_open(self, notification_mock: MagicMock, launch_mock: MagicMock) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest_dir = Path(tmp)
            src = dest_dir / "incoming.bin"
            src.write_text("x")
            plugin = TransferService.__new__(TransferService)
            plugin._agent = MagicMock()
            plugin._agent.transfers = {"/t": {"path": src, "size": 10, "name": "Phone"}}
            plugin._normal_transfers = 0
            plugin._silent_transfers = 1
            plugin._notification = None
            notification_mock.return_value.actions_supported = True
            dst = dest_dir / "out"
            dst.mkdir()
            with patch.object(TransferService, "_make_share_path", return_value=(dst, False)):
                plugin._on_transfer_completed(MagicMock(), "/t", True)
            on_open = notification_mock.return_value.add_action.call_args.args[2]
            on_open("open")
            launch_mock.assert_called_once()
