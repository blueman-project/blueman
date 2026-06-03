from unittest import TestCase
from unittest.mock import patch, Mock

from blueman.plugins.mechanism.Rfcomm import Rfcomm


def _make_rfcomm():
    # MechanismPlugin.__init__ pulls timer/confirm_authorization off parent and
    # calls on_load(), which only registers D-Bus methods on the (mock) parent.
    return Rfcomm(Mock())


class TestOpenRfcomm(TestCase):
    def test_open_spawns_watcher(self):
        rfcomm = _make_rfcomm()
        with patch("blueman.plugins.mechanism.Rfcomm.subprocess.Popen") as popen_mock:
            rfcomm._open_rfcomm(3)
        args = popen_mock.call_args.args[0]
        self.assertEqual(args[-1], "/dev/rfcomm3")

    def test_open_failure_logs_and_propagates(self):
        rfcomm = _make_rfcomm()
        with patch("blueman.plugins.mechanism.Rfcomm.subprocess.Popen",
                   side_effect=OSError("no such file")):
            with self.assertLogs(level="ERROR"):
                with self.assertRaises(OSError):
                    rfcomm._open_rfcomm(0)

    def test_open_fuzz_port_ids(self):
        for port_id in [0, 1, 7, 15, 99, 12345]:
            with self.subTest(port_id=port_id):
                rfcomm = _make_rfcomm()
                with patch("blueman.plugins.mechanism.Rfcomm.subprocess.Popen") as popen_mock:
                    rfcomm._open_rfcomm(port_id)
                self.assertEqual(popen_mock.call_args.args[0][-1], f"/dev/rfcomm{port_id}")
