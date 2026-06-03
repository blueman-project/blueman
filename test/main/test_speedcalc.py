from unittest import TestCase
from unittest.mock import patch

from collections import deque

from blueman.main.SpeedCalc import SAMPLE_RESOLUTION, SpeedCalc


class TestSpeedCalc(TestCase):
    def setUp(self):
        # Drive time.time() deterministically so speed maths are exact.
        self._now = 0.0
        patcher = patch("blueman.main.SpeedCalc.time.time", side_effect=lambda: self._now)
        self.addCleanup(patcher.stop)
        patcher.start()

    def _advance(self, dt):
        self._now = round(self._now + dt, 2)

    def test_first_sample_returns_zero(self):
        sc = SpeedCalc()
        self.assertEqual(sc.calc(100.0), 0)

    def test_first_sample_sets_reference(self):
        sc = SpeedCalc()
        sc.calc(1000.0)
        # Subsequent amounts are measured relative to the first one.
        self.assertEqual(sc.reference, 1000.0)
        self._advance(1.0)
        # Grew by 500 over 1s -> 500/s.
        self.assertEqual(sc.calc(1500.0), 500.0)

    def test_two_samples_speed(self):
        sc = SpeedCalc()
        sc.calc(0.0)
        self._advance(2.0)
        self.assertEqual(sc.calc(2000.0), 1000.0)

    def test_zero_elapsed_time_no_crash(self):
        # Two samples sharing a timestamp must not raise ZeroDivisionError.
        sc = SpeedCalc()
        sc.calc(0.0)
        self.assertEqual(sc.calc(500.0), 0)  # no time advance

    def test_zero_elapsed_after_prune_no_crash(self):
        # Even with many same-timestamp samples it stays safe.
        sc = SpeedCalc(moving_avg=3.0)
        for amount in range(50):
            self.assertEqual(sc.calc(float(amount)), 0)

    def test_reset_clears_log(self):
        sc = SpeedCalc()
        sc.calc(0.0)
        self._advance(1.0)
        sc.calc(100.0)
        sc.reset()
        self.assertEqual(list(sc.log), [])
        # After reset the next sample becomes a fresh reference.
        self.assertEqual(sc.calc(5000.0), 0)
        self.assertEqual(sc.reference, 5000.0)

    def test_log_bounded_under_high_sample_rate(self):
        # Stream many samples; the log must stay bounded to the moving-average
        # window instead of growing without limit.
        sc = SpeedCalc(moving_avg=3.0)
        amount = 0.0
        max_len = 0
        for _ in range(10_000):
            self._advance(0.1)
            amount += 10.0
            sc.calc(amount)
            max_len = max(max_len, len(sc.log))
        # window 3.0s at 0.1s spacing -> ~31 samples; allow a small margin.
        self.assertLessEqual(max_len, 35)

    def test_log_uses_bounded_deque(self):
        sc = SpeedCalc(moving_avg=0.03)
        self.assertIsInstance(sc.log, deque)
        self.assertEqual(sc.log.maxlen, 5)

        for amount in range(10):
            self._advance(SAMPLE_RESOLUTION)
            sc.calc(float(amount))

        max_log_length = sc.log.maxlen
        assert max_log_length is not None
        self.assertLessEqual(len(sc.log), max_log_length)


    def test_log_bounded_with_irregular_gaps(self):
        sc = SpeedCalc(moving_avg=2.0)
        amount = 0.0
        deltas = [0.01, 0.5, 0.01, 0.01, 3.0, 0.01, 0.2, 0.01, 0.01, 1.0]
        max_len = 0
        for i in range(5000):
            self._advance(deltas[i % len(deltas)])
            amount += 1.0
            sc.calc(amount)
            max_len = max(max_len, len(sc.log))
        # Must never grow unbounded regardless of spacing pattern.
        self.assertLessEqual(max_len, 250)

    def test_speed_reflects_recent_window(self):
        sc = SpeedCalc(moving_avg=3.0)
        sc.calc(0.0)
        # Constant 100/s for well beyond the window.
        amount = 0.0
        speed = 0.0
        for _ in range(20):
            self._advance(1.0)
            amount += 100.0
            speed = sc.calc(amount)
        self.assertAlmostEqual(speed, 100.0, places=6)

    def test_fuzz_speed_never_raises_and_is_finite(self):
        import math
        sc = SpeedCalc(moving_avg=1.5)
        # Pseudo-random but deterministic deltas/amounts.
        amount = 0.0
        delta_cycle = [0.0, 0.01, 0.1, 0.37, 1.0, 2.5, 0.0, 0.05]
        amount_cycle = [0.0, 1.0, -1.0, 1000.0, 0.5, 1e6, 3.3, 42.0]
        for i in range(3000):
            self._advance(delta_cycle[i % len(delta_cycle)])
            amount += amount_cycle[i % len(amount_cycle)]
            speed = sc.calc(amount)
            self.assertIsInstance(speed, (int, float))
            self.assertFalse(math.isnan(float(speed)))
            self.assertFalse(math.isinf(float(speed)))
            max_log_length = sc.log.maxlen
            assert max_log_length is not None
            self.assertLessEqual(len(sc.log), max_log_length)
