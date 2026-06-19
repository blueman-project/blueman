from unittest import TestCase
from unittest.mock import Mock, patch

from blueman.main.Sendto import Sender, SendTo


def make_sender() -> Sender:
    """Build a Sender without running its GTK/D-Bus __init__.

    Only the attributes touched by the method under test are populated; the
    progress bar and speed calculator are mocks.
    """
    s = Sender.__new__(Sender)
    s.pb = Mock()
    s.speed = Mock()
    s.speed.calc.return_value = 1000.0
    s.num_files = 1
    s.files = [Mock()]
    s.total_bytes = 10000
    s.total_transferred = 0
    s.transferred = 0
    s._last_bytes = 0
    s._last_update = 0.0
    return s


class TestOnTransferProgressClock(TestCase):
    @patch("blueman.main.Sendto.time.monotonic")
    def test_throttle_uses_monotonic(self, monotonic: Mock) -> None:
        s = make_sender()
        # First tick at t=100: _last_update is 0.0 so the update fires.
        monotonic.return_value = 100.0
        s.on_transfer_progress(None, 500)
        self.assertEqual(s._last_update, 100.0)
        self.assertEqual(s.speed.calc.call_count, 1)

        # 0.2s later: below the 0.5s threshold, no further speed/ETA update.
        monotonic.return_value = 100.2
        s.on_transfer_progress(None, 800)
        self.assertEqual(s.speed.calc.call_count, 1)
        self.assertEqual(s._last_update, 100.0)

        # 0.6s after the last update: fires again.
        monotonic.return_value = 100.6
        s.on_transfer_progress(None, 1200)
        self.assertEqual(s.speed.calc.call_count, 2)
        self.assertEqual(s._last_update, 100.6)

    @patch("blueman.main.Sendto.time.monotonic", return_value=5.0)
    def test_progress_accumulates_and_sets_fraction(self, _monotonic: Mock) -> None:
        s = make_sender()
        s.on_transfer_progress(None, 2500)
        self.assertEqual(s.total_transferred, 2500)
        self.assertEqual(s._last_bytes, 2500)
        self.assertAlmostEqual(s.pb.props.fraction, 0.25)  # 2500 / 10000


def make_sendto() -> SendTo:
    s = SendTo.__new__(SendTo)
    s._device_selector = Mock()
    s._manager = Mock()
    return s


class TestManagerSignalDispatch(TestCase):
    @patch("blueman.main.Sendto.GLib.timeout_add_seconds")
    def test_adapter_added(self, timeout: Mock) -> None:
        s = make_sendto()
        s._SendTo__on_manager_signal(None, "/org/bluez/hci0", "adapter-added")
        s._device_selector.add_adapter.assert_called_once_with("/org/bluez/hci0")
        timeout.assert_called_once()

    def test_adapter_removed(self) -> None:
        s = make_sendto()
        s._SendTo__on_manager_signal(None, "/org/bluez/hci0", "adapter-removed")
        s._device_selector.remove_adapter.assert_called_once_with("/org/bluez/hci0")

    def test_device_added_sets_warning(self) -> None:
        s = make_sendto()
        s._has_objpush = Mock(return_value=False)  # type: ignore[method-assign]
        s._SendTo__on_manager_signal(None, "/dev/x", "device-added")
        s._device_selector.add_device.assert_called_once_with("/dev/x", True)

    def test_device_removed(self) -> None:
        s = make_sendto()
        s._SendTo__on_manager_signal(None, "/dev/x", "device-removed")
        s._device_selector.remove_device.assert_called_once_with("/dev/x")

    def test_unknown_signal_raises(self) -> None:
        s = make_sendto()
        with self.assertRaises(ValueError):
            s._SendTo__on_manager_signal(None, "/dev/x", "bogus")


class TestPropertyChangedDispatch(TestCase):
    def test_adapter_discovering(self) -> None:
        s = make_sendto()
        s._SendTo__on_adapter_property_changed(None, "Discovering", True, "/org/bluez/hci0")
        s._device_selector.set_discovering.assert_called_once_with(True)

    def test_adapter_other_key_ignored(self) -> None:
        s = make_sendto()
        s._SendTo__on_adapter_property_changed(None, "Powered", True, "/org/bluez/hci0")
        s._device_selector.set_discovering.assert_not_called()

    def test_device_alias(self) -> None:
        s = make_sendto()
        s._SendTo__on_device_property_changed(None, "Alias", "Phone", "/dev/x")
        s._device_selector.update_row.assert_called_once_with("/dev/x", "description", "Phone")

    def test_device_uuids_updates_warning(self) -> None:
        s = make_sendto()
        s._has_objpush = Mock(return_value=True)  # type: ignore[method-assign]
        s._SendTo__on_device_property_changed(None, "UUIDs", ["x"], "/dev/x")
        s._device_selector.update_row.assert_called_once_with("/dev/x", "warning", False)


class TestStartDiscovery(TestCase):
    def test_starts_only_idle_adapters_and_return_value(self) -> None:
        s = make_sendto()
        a_idle = Mock()
        a_idle.__getitem__ = Mock(return_value=False)
        a_busy = Mock()
        a_busy.__getitem__ = Mock(return_value=True)
        s._manager.get_adapters.return_value = [a_idle, a_busy]

        self.assertTrue(s._start_discovery())          # not from timer -> repeat
        a_idle.start_discovery.assert_called_once_with()
        a_busy.start_discovery.assert_not_called()

        self.assertFalse(s._start_discovery(from_timer=True))  # one-shot


class TestSenderQueueAndText(TestCase):
    def test_update_pb_text_format(self) -> None:
        s = make_sender()
        s.num_files = 3
        s.files = [Mock(), Mock()]  # one already sent -> num = 3-2+1 = 2
        s._update_pb_text(1.5, "KB", "5 Seconds")
        text = s.pb.set_text.call_args.args[0]
        self.assertIn("2/3", text)
        self.assertIn("1.50", text)
        self.assertIn("KB", text)
        self.assertIn("5 Seconds", text)

    def test_update_pb_text_infinite_eta(self) -> None:
        s = make_sender()
        s.num_files = 1
        s.files = [Mock()]
        s._update_pb_text(0.0, "B")
        self.assertIn("∞", s.pb.set_text.call_args.args[0])

    def test_process_queue_sends_next(self) -> None:
        s = Sender.__new__(Sender)
        f = Mock()
        f.get_path.return_value = "/tmp/file"
        s.files = [f]
        s.send_file = Mock()  # type: ignore[method-assign]
        s.process_queue()
        s.send_file.assert_called_once_with("/tmp/file")

    def test_process_queue_emits_result_when_done(self) -> None:
        s = Sender.__new__(Sender)
        s.files = []
        s.emit = Mock()  # type: ignore[method-assign]
        s.process_queue()
        s.emit.assert_called_once_with("result", True)

    def test_on_transfer_completed_pops_and_continues(self) -> None:
        s = Sender.__new__(Sender)
        s.files = [Mock(), Mock()]
        s.process_queue = Mock()  # type: ignore[method-assign]
        s.on_transfer_completed(None)
        self.assertEqual(len(s.files), 1)
        self.assertIsNone(s.transfer)
        s.process_queue.assert_called_once_with()


class TestCreateSessionTimeout(TestCase):
    def test_creates_session_once_and_stops(self) -> None:
        s = Sender.__new__(Sender)
        s.create_session = Mock()  # type: ignore[method-assign]
        result = s._create_session_timeout()
        s.create_session.assert_called_once_with()
        # Must return False so the GLib timeout does not repeat.
        self.assertFalse(result)


class TestSetupSignalHandlers(TestCase):
    def test_connects_each_signal_with_args(self) -> None:
        source = Mock()
        cb1, cb2 = Mock(), Mock()
        SendTo._setup_signal_handlers(source, {
            "adapter-added": (cb1, "adapter-added"),
            "property-changed": (cb2,),
        })
        source.connect.assert_any_call("adapter-added", cb1, "adapter-added")
        source.connect.assert_any_call("property-changed", cb2)
        self.assertEqual(source.connect.call_count, 2)

    def test_empty_handlers_no_calls(self) -> None:
        source = Mock()
        SendTo._setup_signal_handlers(source, {})
        source.connect.assert_not_called()


OBJPUSH_UUID = "00001105-0000-1000-8000-00805f9b34fb"
GATT_UUID = "00001801-0000-1000-8000-00805f9b34fb"


class TestHasObjpush(TestCase):
    @patch("blueman.main.Sendto.Device")
    def test_true_when_objpush_present(self, device_cls: Mock) -> None:
        device_cls.return_value = {"UUIDs": [GATT_UUID, OBJPUSH_UUID]}
        s = SendTo.__new__(SendTo)
        self.assertTrue(s._has_objpush("/org/bluez/hci0/dev_AA"))

    @patch("blueman.main.Sendto.Device")
    def test_false_when_absent(self, device_cls: Mock) -> None:
        device_cls.return_value = {"UUIDs": [GATT_UUID]}
        s = SendTo.__new__(SendTo)
        self.assertFalse(s._has_objpush("/org/bluez/hci0/dev_AA"))

    @patch("blueman.main.Sendto.Device")
    def test_false_when_empty(self, device_cls: Mock) -> None:
        device_cls.return_value = {"UUIDs": []}
        s = SendTo.__new__(SendTo)
        self.assertFalse(s._has_objpush("/org/bluez/hci0/dev_AA"))


class TestOnTransferProgressGuards(TestCase):
    @patch("blueman.main.Sendto.time.monotonic", return_value=1.0)
    def test_zero_speed_no_zero_division(self, _monotonic: Mock) -> None:
        s = make_sender()
        s.speed.calc.return_value = 0.0
        # ETA cannot be computed; must not raise, must log, must still render.
        with self.assertLogs(level="DEBUG"):
            s.on_transfer_progress(None, 100)
        self.assertTrue(s.pb.set_text.called)

    @patch("blueman.main.Sendto.time.monotonic", return_value=1.0)
    def test_zero_total_bytes_no_zero_division(self, _monotonic: Mock) -> None:
        s = make_sender()
        s.total_bytes = 0
        s.speed.calc.return_value = 0.0
        # Must not raise ZeroDivisionError on the fraction update.
        s.on_transfer_progress(None, 0)
        # fraction left untouched (never divided by zero).

    @patch("blueman.main.Sendto.time.monotonic", return_value=1.0)
    def test_positive_speed_computes_eta(self, _monotonic: Mock) -> None:
        s = make_sender()
        s.total_bytes = 100000
        s.speed.calc.return_value = 1000.0
        s.on_transfer_progress(None, 1000)
        # ETA computed, progress bar text updated.
        self.assertTrue(s.pb.set_text.called)
