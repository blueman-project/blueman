import signal
from unittest import TestCase
from unittest.mock import patch, Mock

from blueman.plugins.mechanism.Rfcomm import Rfcomm


def _make_rfcomm():
    # MechanismPlugin.__init__ pulls timer/confirm_authorization off parent and
    # calls on_load(), which only registers D-Bus methods on the (mock) parent.
    return Rfcomm(Mock())


def _popen_returning(ps_output: str):
    proc = Mock()
    proc.communicate.return_value = (ps_output.encode("UTF-8"), None)
    return Mock(return_value=proc)


class TestCloseRfcomm(TestCase):
    def _run(self, ps_output: str, port_id: int = 0):
        rfcomm = _make_rfcomm()
        with patch("blueman.plugins.mechanism.Rfcomm.subprocess.Popen",
                   _popen_returning(ps_output)), \
                patch("blueman.plugins.mechanism.Rfcomm.os.kill") as kill_mock:
            rfcomm._close_rfcomm(port_id)
        return kill_mock

    def test_kills_matching_watcher(self):
        ps = (
            "  PID COMMAND\n"
            " 1234 blueman-rfcomm-watcher /dev/rfcomm0\n"
            " 5678 some other process\n"
        )
        kill_mock = self._run(ps, port_id=0)
        kill_mock.assert_called_once_with(1234, signal.SIGTERM)

    def test_no_match_no_kill(self):
        ps = " 1234 blueman-rfcomm-watcher /dev/rfcomm9\n"
        kill_mock = self._run(ps, port_id=0)
        kill_mock.assert_not_called()

    def test_multiple_matches(self):
        ps = (
            " 100 blueman-rfcomm-watcher /dev/rfcomm0\n"
            " 200 blueman-rfcomm-watcher /dev/rfcomm0\n"
        )
        kill_mock = self._run(ps, port_id=0)
        self.assertEqual(kill_mock.call_count, 2)

    def test_malformed_lines_do_not_crash(self):
        # Blank line, header, single-field line, non-numeric pid -- all must be
        # skipped rather than raising ValueError.
        ps = (
            "\n"
            "PID COMMAND\n"
            "justonetoken\n"
            "notapid blueman-rfcomm-watcher /dev/rfcomm0\n"
            "   \n"
            " 4242 blueman-rfcomm-watcher /dev/rfcomm0\n"
        )
        kill_mock = self._run(ps, port_id=0)
        # Only the well-formed numeric-pid match is killed.
        kill_mock.assert_called_once_with(4242, signal.SIGTERM)

    def test_empty_output(self):
        kill_mock = self._run("", port_id=0)
        kill_mock.assert_not_called()

    def test_fuzz_arbitrary_ps_output_never_raises(self):
        fragments = [
            "", " ", "\t", "\n", "PID COMMAND", "0", "-1 x", "x x x",
            "999999999999999999999 cmd", "12 a b c d e",
            " 12 blueman-rfcomm-watcher /dev/rfcomm0",
            "12\tblueman-rfcomm-watcher /dev/rfcomm0",
            "  ��  ", "1.5 cmd", "+12 cmd", "0x10 cmd",
        ]
        # Build many pseudo-random line combinations deterministically.
        for i in range(len(fragments)):
            for j in range(len(fragments)):
                ps = "\n".join([fragments[i], fragments[j], fragments[(i + j) % len(fragments)]])
                with self.subTest(i=i, j=j):
                    # Must not raise for any combination.
                    self._run(ps, port_id=i % 3)
