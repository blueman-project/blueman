# Copyright (C) 2008 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2008 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

import time

class SpeedCalc:
	
	def __init__(self, moving_avg = 3):
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
			#print "tt "+str(total_time)
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

