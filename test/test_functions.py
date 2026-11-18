import errno
import os

from pathlib import Path
from tempfile import TemporaryDirectory, TemporaryFile
from unittest import TestCase
from unittest.mock import patch

import blueman.Functions as Functions


class TestAdapterPathToName(TestCase):
    def test_matches_hci(self):
        self.assertEqual(Functions.adapter_path_to_name("/path/hci9"), "hci9")

    def test_returns_none_for_empty_or_none(self):
        self.assertIsNone(Functions.adapter_path_to_name(None))
        self.assertIsNone(Functions.adapter_path_to_name(""))

    def test_no_match(self):
        self.assertIsNone(Functions.adapter_path_to_name("regular/path"))


class TestE_(TestCase):
    def test_string_input(self):
        msg, tb = Functions.e_("error: some message")
        self.assertEqual(msg, "some message")
        self.assertIsNone(tb)

    def test_simple_string(self):
        msg, tb = Functions.e_("simple error")
        self.assertEqual(msg, "simple error")
        self.assertIsNone(tb)

    def test_exception_input(self):
        exc = ValueError("test error")
        msg, tb = Functions.e_(exc)
        self.assertEqual(msg, "test error")
        self.assertIsNotNone(tb)


class TestFormatBytes(TestCase):
    def test_bytes(self):
        val, suffix = Functions.format_bytes(500)
        self.assertEqual(val, 500.0)
        self.assertEqual(suffix, "B")

    def test_kb(self):
        val, suffix = Functions.format_bytes(2048)
        self.assertAlmostEqual(val, 2.0)
        self.assertEqual(suffix, "KB")

    def test_mb(self):
        val, suffix = Functions.format_bytes(1024 * 1024 + 1024)
        self.assertGreater(val, 1.0)
        self.assertEqual(suffix, "MB")

    def test_gb(self):
        val, suffix = Functions.format_bytes(1024 ** 3 + 1024 ** 2)
        self.assertGreater(val, 1.0)
        self.assertEqual(suffix, "GB")


class TestHave(TestCase):
    def setUp(self):
        self.env_path = {'PATH': '/usr/bin:/sbin'}

    def test_path_exists(self):
        with patch.dict(os.environ, self.env_path), \
             patch.object(Path, "exists", return_value=True), \
             patch.object(os, "access", return_value=True):

            result = Functions.have("executable")
            self.assertIsNotNone(result)
            self.assertEqual(result, Path("/usr/bin/executable"))

    def test_path_does_not_exist(self):
        with patch.dict(os.environ, self.env_path), \
             patch.object(Path, "exists", return_value=False):

            result = Functions.have("executable")
            self.assertIsNone(result)

    def test_path_not_executable(self):
        with patch.dict(os.environ, self.env_path), \
             patch.object(Path, "exists", return_value=True), \
             patch.object(os, "access", return_value=False):

            result = Functions.have("executable")
            self.assertIsNone(result)


class TestBmexit(TestCase):
    def test_exit_with_message(self):
        with self.assertRaises(SystemExit) as ctx:
            Functions.bmexit("test exit")
        self.assertEqual(ctx.exception.code, "test exit")

    def test_exit_none(self):
        with self.assertRaises(SystemExit) as ctx:
            Functions.bmexit(None)
        self.assertIsNone(ctx.exception.code)


class TestPluginNames(TestCase):
    def setUp(self) -> None:
        self.tempdir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_plugins(self):
        for name in ("plugin_a.py", "plugin_b.py", "__init__.py"):
            Path(self.tempdir.name).joinpath(name).touch()

        result = Functions.plugin_names(Path(self.tempdir.name) / "__init__.py")
        # names can be in any order
        self.assertIn("plugin_a", result)
        self.assertIn("plugin_b", result)
        self.assertNotIn("__init__", result)
        self.assertCountEqual(result, ["plugin_a", "plugin_b"])

    def test_no_plugins(self):
        result = Functions.plugin_names(Path(self.tempdir.name) / "__init__.py")
        self.assertEqual(result, [])


class TestOpenRfcomm(TestCase):
    def setUp(self):
        self.fake_rfcomm = TemporaryFile()

    def tearDown(self):
        self.fake_rfcomm.close()

    @patch("blueman.Functions.sleep")
    def test_open_success(self, mock_sleep):
        with patch('os.open', return_value=42) as mock_open:
            fd = Functions.open_rfcomm(self.fake_rfcomm.name, rw=True)
            self.assertEqual(fd, 42)
            mock_open.assert_called_once()

    @patch("blueman.Functions.sleep")
    def test_open_busy_then_success(self, mock_sleep):
        with patch('os.open') as mock_open:
            # First call raises EBUSY, second succeeds
            mock_open.side_effect = [OSError(errno.EBUSY, "file busy"), 42]

            fd = Functions.open_rfcomm(self.fake_rfcomm.name)

            self.assertEqual(fd, 42)
            self.assertEqual(mock_sleep.call_count, 1)
            mock_sleep.assert_called_with(2)

    @patch("blueman.Functions.sleep")
    def test_open_other_error(self, mock_sleep):
        with patch('os.open', side_effect=OSError(errno.ENOENT, "no such file")):
            with self.assertRaises(OSError) as context:
                Functions.open_rfcomm(self.fake_rfcomm.name)
            self.assertEqual(context.exception.errno, errno.ENOENT)
