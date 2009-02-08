#
#
# speed_calc.py
# (c) 2007 Valmantas Paliksa <walmis at balticum-tv dot lt>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
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

