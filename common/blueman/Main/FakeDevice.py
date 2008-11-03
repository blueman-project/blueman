

class FakeDevice:
	
	def __init__(self, info):
		self.info = info
		
	def GetProperties(self):
		return self.info
