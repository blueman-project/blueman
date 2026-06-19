from unittest import TestCase

from blueman.Functions import adapter_path_to_name, format_bytes


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
