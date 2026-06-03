import math
import time
from collections import deque


SAMPLE_RESOLUTION = 0.01


class SpeedCalc:
    def __init__(self, moving_avg: float = 3.0) -> None:
        self.moving_avg = moving_avg
        max_log_length = max(2, math.ceil(self.moving_avg / SAMPLE_RESOLUTION) + 2)
        self.log: deque[tuple[float, float]] = deque(maxlen=max_log_length)

        self.reference: float = 0

    def calc(self, amount: float) -> float:
        if not self.log:
            self.reference = amount
        amount -= self.reference
        curtime = round(time.time(), 2)
        self.log.append((curtime, amount))

        # Drop samples that fall outside the moving-average window, always
        # keeping at least two so a speed can still be computed. This bounds
        # the log length to the window regardless of the sampling rate (the
        # previous code only dropped a single sample per call).
        while len(self.log) > 2 and curtime - self.log[1][0] >= self.moving_avg:
            self.log.popleft()

        if len(self.log) < 2:
            return 0

        total_time = self.log[-1][0] - self.log[0][0]
        if total_time <= 0:
            # All retained samples share a timestamp (e.g. sub-resolution
            # calls); avoid dividing by zero until time has advanced.
            return 0

        total_amount = self.log[-1][1] - self.log[0][1]
        return total_amount / total_time

    def reset(self) -> None:
        self.log.clear()
