from unittest import TestCase

from blueman.Functions import format_bytes


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
