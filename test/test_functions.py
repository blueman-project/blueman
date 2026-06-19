import logging
import os
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from blueman.Functions import adapter_path_to_name, create_logger, format_bytes, have, parse_os_release


class TestFormatBytes(TestCase):
    def test_zero(self) -> None:
        self.assertEqual(format_bytes(0), (0.0, "B"))

    def test_sub_kilobyte(self) -> None:
        self.assertEqual(format_bytes(512), (512.0, "B"))
        self.assertEqual(format_bytes(1023), (1023.0, "B"))

    def test_kilobyte_boundary(self) -> None:
        # Regression: exact 1024 must be 1.0 KB, not a fraction of a GB.
        self.assertEqual(format_bytes(1024), (1.0, "KB"))

    def test_megabyte_boundary(self) -> None:
        self.assertEqual(format_bytes(1024 * 1024), (1.0, "MB"))

    def test_gigabyte_boundary(self) -> None:
        self.assertEqual(format_bytes(1024 * 1024 * 1024), (1.0, "GB"))

    def test_mid_band_values(self) -> None:
        self.assertEqual(format_bytes(1536), (1.5, "KB"))
        self.assertEqual(format_bytes(1024 * 1024 * 3), (3.0, "MB"))

    def test_huge_value(self) -> None:
        ret, suffix = format_bytes(5 * 1024 ** 4)
        self.assertEqual(suffix, "GB")
        self.assertEqual(ret, 5 * 1024)

    def test_accepts_float_and_int(self) -> None:
        self.assertEqual(format_bytes(2048.0), (2.0, "KB"))
        self.assertEqual(format_bytes(2048), (2.0, "KB"))


class TestAdapterPathToName(TestCase):
    def test_normal_path(self) -> None:
        self.assertEqual(adapter_path_to_name("/org/bluez/hci0"), "hci0")

    def test_none_and_empty(self) -> None:
        self.assertIsNone(adapter_path_to_name(None))
        self.assertIsNone(adapter_path_to_name(""))

    def test_no_hci(self) -> None:
        self.assertIsNone(adapter_path_to_name("/org/bluez"))
        self.assertIsNone(adapter_path_to_name("no-match"))

    def test_case_sensitive(self) -> None:
        # The pattern matches lowercase "hci" only.
        self.assertIsNone(adapter_path_to_name("HCI0"))

    def test_trailing_segments(self) -> None:
        # Device sub-paths still resolve to the adapter name.
        self.assertEqual(adapter_path_to_name("/org/bluez/hci0/dev_AA_BB_CC_DD_EE_FF"), "hci0")

    def test_zero_digits_allowed(self) -> None:
        # The `[0-9]*` quantifier permits an "hci" with no index.
        self.assertEqual(adapter_path_to_name("/org/bluez/hci"), "hci")
        self.assertEqual(adapter_path_to_name("hci"), "hci")

    def test_greedy_picks_last_occurrence(self) -> None:
        # Greedy `.*` consumes up to the final "hci" match.
        self.assertEqual(adapter_path_to_name("/org/bluez/hci0hci1"), "hci1")

    def test_embedded_in_other_text(self) -> None:
        self.assertEqual(adapter_path_to_name("prefix-hci99-suffix"), "hci99")


class TestParseOsRelease(TestCase):
    def _parse(self, content: str) -> dict[str, str]:
        with tempfile.NamedTemporaryFile("w", suffix="os-release", delete=False) as f:
            f.write(content)
            path = Path(f.name)
        try:
            return parse_os_release(path)
        finally:
            path.unlink()

    def test_basic_keys(self) -> None:
        result = self._parse('NAME="Foo"\nVERSION="1.0"\n')
        self.assertEqual(result, {"NAME": "Foo", "VERSION": "1.0"})

    def test_value_with_equals_sign(self) -> None:
        # Regression (data-3): a quoted value containing "=" must survive.
        result = self._parse('PRETTY_NAME="Name=Variant"\n')
        self.assertEqual(result["PRETTY_NAME"], "Name=Variant")

    def test_unquoted_value(self) -> None:
        self.assertEqual(self._parse("ID=arch\n"), {"ID": "arch"})

    def test_comments_and_blank_lines_skipped(self) -> None:
        result = self._parse("# comment\n\n   \nID=foo\n")
        self.assertEqual(result, {"ID": "foo"})

    def test_line_without_equals_skipped(self) -> None:
        result = self._parse("garbage line\nID=foo\n")
        self.assertEqual(result, {"ID": "foo"})

    def test_missing_file_returns_empty(self) -> None:
        self.assertEqual(parse_os_release(Path("/nonexistent/os-release")), {})


class TestHave(TestCase):
    @patch("blueman.Functions.shutil.which", return_value="/usr/bin/dhclient")
    def test_found_returns_path(self, which: object) -> None:
        result = have("dhclient")
        self.assertEqual(result, Path("/usr/bin/dhclient"))

    @patch("blueman.Functions.shutil.which", return_value=None)
    def test_not_found_returns_none(self, which: object) -> None:
        self.assertIsNone(have("nonexistent-binary"))

    @patch.dict(os.environ, {"PATH": "/usr/bin"}, clear=True)
    @patch("blueman.Functions.shutil.which", return_value=None)
    def test_appends_sbin_dirs(self, which: object) -> None:
        have("dhcpcd")
        used_path = which.call_args.kwargs["path"]
        parts = used_path.split(os.pathsep)
        self.assertIn("/usr/bin", parts)
        self.assertIn("/sbin", parts)
        self.assertIn("/usr/sbin", parts)

    @patch.dict(os.environ, {"PATH": "/sbin:/usr/sbin:/usr/bin"}, clear=True)
    @patch("blueman.Functions.shutil.which", return_value=None)
    def test_does_not_duplicate_existing_sbin(self, which: object) -> None:
        have("udhcpc")
        used_path = which.call_args.kwargs["path"]
        self.assertEqual(used_path.split(os.pathsep).count("/sbin"), 1)
        self.assertEqual(used_path.split(os.pathsep).count("/usr/sbin"), 1)


class TestCreateLogger(TestCase):
    def setUp(self) -> None:
        root = logging.getLogger(None)
        self._saved_handlers = root.handlers[:]
        self._saved_name = root.name
        self._saved_level = root.level

    def tearDown(self) -> None:
        root = logging.getLogger(None)
        root.handlers[:] = self._saved_handlers
        root.name = self._saved_name
        root.level = self._saved_level

    @patch("blueman.Functions.logging.handlers.SysLogHandler")
    def test_syslog_handler_added_when_available(self, handler_cls: MagicMock) -> None:
        handler_cls.return_value = logging.NullHandler()
        create_logger(logging.INFO, "blueman-test", syslog=True)
        handler_cls.assert_called_once_with(address="/dev/log")

    @patch("blueman.Functions.logging.handlers.SysLogHandler", side_effect=OSError)
    def test_falls_back_to_stderr_when_dev_log_missing(self, handler_cls: MagicMock) -> None:
        # Must not raise when /dev/log is unavailable, and add no syslog handler.
        before = len(logging.getLogger(None).handlers)
        logger = create_logger(logging.INFO, "blueman-test", syslog=True)
        handler_cls.assert_called_once_with(address="/dev/log")
        self.assertLessEqual(len(logger.handlers), before + 1)  # only basicConfig's stderr handler, if any

    @patch("blueman.Functions.logging.handlers.SysLogHandler")
    def test_no_syslog_handler_when_disabled(self, handler_cls: MagicMock) -> None:
        create_logger(logging.INFO, "blueman-test", syslog=False)
        handler_cls.assert_not_called()
