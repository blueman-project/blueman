import time
from typing import List, Tuple


class SpeedCalc:
    def __init__(self, moving_avg: float = 3.0) -> None:
        self.moving_avg = moving_avg
        self.log: List[Tuple[float, float]] = []

        self.reference: float = 0

    def calc(self, amount: float) -> float:
        if not self.log:
            self.reference = amount
        amount -= self.reference
        curtime = round(time.time(), 2)
        self.log.append((curtime, amount))
        if len(self.log) >= 2:
            total_time = self.log[-1][0] - self.log[0][0]
            # print "tt "+str(total_time)
            if total_time >= self.moving_avg:
                total_amount = self.log[-1][1] - self.log[0][1]

                speed = total_amount / total_time
                del self.log[0]
                return speed

            else:
                total_amount = self.log[-1][1] - self.log[0][1]
                speed = total_amount / total_time
                return speed

        else:
            return 0

    def reset(self) -> None:
        self.log = []
