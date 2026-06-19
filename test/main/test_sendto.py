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
