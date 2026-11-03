import unittest

from blueman.main.Sendto import format_transfer_status


class TestTransferStatus(unittest.TestCase):
    def test_unknown_measurements_are_omitted(self) -> None:
        status = format_transfer_status(1, 3)
        self.assertEqual(status, "Sending file 1 of 3")
        self.assertNotIn("∞", status)
        self.assertNotIn("ETA", status)

    def test_real_speed_and_eta_are_shown(self) -> None:
        status = format_transfer_status(2, 3, 1.25, "MB", "8 Seconds")
        self.assertIn("1.25 MB/s", status)
        self.assertIn("ETA: 8 Seconds", status)


if __name__ == "__main__":
    unittest.main()
