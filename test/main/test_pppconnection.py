import errno
from unittest import TestCase
from unittest.mock import patch, Mock

from gi.repository import GLib

from blueman.main.PPPConnection import PPPConnection, PPPException


def _cgdcont_commands(conn: PPPConnection):
    return [c for c in conn.commands if isinstance(c, str) and c.startswith("AT+CGDCONT")]


def _capture_errors(conn: PPPConnection):
    errors = []
    conn.connect("error-occurred", lambda _conn, message: errors.append(message))
    return errors


class TestPPPConnectionApn(TestCase):
    def test_empty_apn_adds_no_cgdcont(self):
        conn = PPPConnection("/dev/rfcomm0", apn="")
        self.assertEqual(_cgdcont_commands(conn), [])

    def test_valid_apn_builds_quoted_command(self):
        conn = PPPConnection("/dev/rfcomm0", apn="internet")
        self.assertIn('AT+CGDCONT=1,"IP","internet"', conn.commands)

    def test_valid_apns_accepted(self):
        for apn in [
            "internet", "web.provider.com", "a-b.c", "APN123", "3g.example",
            "123456", "UPPERCASE.APN", "apn.v1-2.test", "",
        ]:
            with self.subTest(apn=apn):
                PPPConnection("/dev/rfcomm0", apn=apn)

    def test_invalid_apn_rejected(self):
        for apn in [
            'foo","extra',          # quote break-out
            "foo bar",              # space
            "foo;reboot",
            "foo\nAT+X",            # newline injection
            'a"b',
            "foo/bar",
            "café",
            "foo\tbar",
            "foo,bar",
            "apn'quote",
            "apn$variable",
            "apn&background",
            "apn(parens)",
            "apn#hash",
            "apn!bang",
            "apn@at",
            "apn\rtrailer"
        ]:
            with self.subTest(apn=apn):
                with self.assertRaises(PPPException):
                    PPPConnection("/dev/rfcomm0", apn=apn)

    def test_rejected_apn_never_reaches_command(self):
        # Defence in depth: an injection payload must never end up in a command.
        with self.assertRaises(PPPException):
            PPPConnection("/dev/rfcomm0", apn='x","IP","evil')

    def test_fuzz_apn_no_unexpected_exception(self):
        samples = [
            "", "a", "A.B-C", "1234567890", "x" * 200,
            "with space", "tab\tchar", "new\nline", 'quote"', "semi;colon",
            "slash/", "comma,", "unicode-café", "null\x00byte", "%s%n",
            "../../etc", "$(id)", "`id`", "&&ls",
        ]
        for apn in samples:
            with self.subTest(apn=apn):
                try:
                    conn = PPPConnection("/dev/rfcomm0", apn=apn)
                except PPPException:
                    continue
                # If accepted, the APN must be the safe charset and round-trip
                # verbatim into exactly one quoted command.
                cmds = _cgdcont_commands(conn)
                if apn == "":
                    self.assertEqual(cmds, [])
                else:
                    self.assertEqual(cmds, [f'AT+CGDCONT=1,"IP","{apn}"'])


class TestPPPConnectionCrashGuards(TestCase):
    def test_lifecycle_attributes_are_initialized(self):
        conn = PPPConnection("/dev/rfcomm0")

        self.assertIsNone(conn.file)
        self.assertIsNone(conn.pppd)
        self.assertIsNone(conn.io_watch)
        self.assertIsNone(conn.timeout)
        self.assertEqual(conn.buffer, "")

    def test_cleanup_without_open_file_does_not_raise(self):
        PPPConnection("/dev/rfcomm0").cleanup()

    @patch("blueman.main.PPPConnection.os.close")
    def test_cleanup_closes_open_file_once(self, close_mock):
        conn = PPPConnection("/dev/rfcomm0")
        conn.file = 42

        conn.cleanup()
        conn.cleanup()

        close_mock.assert_called_once_with(42)
        self.assertIsNone(conn.file)

    @patch("blueman.main.PPPConnection.os.close", side_effect=OSError("bad fd"))
    def test_cleanup_clears_file_after_close_error(self, close_mock):
        conn = PPPConnection("/dev/rfcomm0")
        conn.file = 42

        with self.assertLogs(level="ERROR"):
            conn.cleanup()

        close_mock.assert_called_once_with(42)
        self.assertIsNone(conn.file)

    def test_check_pppd_before_spawn_stops_polling(self):
        self.assertFalse(PPPConnection("/dev/rfcomm0").check_pppd())

    @patch("blueman.main.PPPConnection.os.close")
    @patch("blueman.main.PPPConnection.GLib.source_remove")
    def test_socket_condition_removes_timeout_and_closes_file(self, source_remove_mock, close_mock):
        conn = PPPConnection("/dev/rfcomm0")
        conn.file = 42
        conn.timeout = 99
        errors = _capture_errors(conn)

        keep = conn.on_data_ready(42, GLib.IO_HUP, 0)

        self.assertFalse(keep)
        source_remove_mock.assert_called_once_with(99)
        close_mock.assert_called_once_with(42)
        self.assertIsNone(conn.timeout)
        self.assertIsNone(conn.file)
        self.assertEqual(errors, ["Socket error"])

    @patch("blueman.main.PPPConnection.os.close")
    @patch("blueman.main.PPPConnection.os.read", side_effect=OSError(errno.EBADF, "bad fd"))
    @patch("blueman.main.PPPConnection.GLib.source_remove")
    def test_read_error_removes_timeout_and_closes_file(self, source_remove_mock, read_mock, close_mock):
        conn = PPPConnection("/dev/rfcomm0")
        conn.file = 42
        conn.timeout = 99
        errors = _capture_errors(conn)

        with self.assertLogs(level="ERROR"):
            keep = conn.on_data_ready(42, 0, 0)

        self.assertFalse(keep)
        read_mock.assert_called_once_with(42, 1)
        source_remove_mock.assert_called_once_with(99)
        close_mock.assert_called_once_with(42)
        self.assertIsNone(conn.timeout)
        self.assertIsNone(conn.file)
        self.assertEqual(errors, ["Socket error"])

    @patch("blueman.main.PPPConnection.os.close")
    @patch("blueman.main.PPPConnection.GLib.source_remove")
    @patch("blueman.main.PPPConnection.GLib.io_add_watch", return_value=11)
    def test_wait_timeout_removes_io_watch_and_closes_file(self, io_add_watch_mock, source_remove_mock, close_mock):
        timeout_callbacks = []

        def capture_timeout(_interval, callback):
            timeout_callbacks.append(callback)
            return 22

        conn = PPPConnection("/dev/rfcomm0")
        conn.file = 42
        errors = _capture_errors(conn)

        with patch("blueman.main.PPPConnection.GLib.timeout_add", side_effect=capture_timeout):
            conn.wait_for_reply(0)

        self.assertEqual(conn.io_watch, 11)
        self.assertEqual(conn.timeout, 22)
        self.assertEqual(len(timeout_callbacks), 1)

        keep = timeout_callbacks[0]()

        self.assertFalse(keep)
        io_add_watch_mock.assert_called_once()
        source_remove_mock.assert_called_once_with(11)
        close_mock.assert_called_once_with(42)
        self.assertIsNone(conn.io_watch)
        self.assertIsNone(conn.timeout)
        self.assertIsNone(conn.file)
        self.assertEqual(errors, ["Modem initialization timed out"])
