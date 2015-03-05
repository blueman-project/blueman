from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import time


class SpeedCalc:
    def __init__(self, moving_avg=3):
        self.moving_avg = moving_avg
        self.log = []

        self.reference = 0

    def calc(self, amount):
        if self.log == []:
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

    def reset(self):
        self.log = []

