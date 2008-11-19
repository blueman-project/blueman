

class FakeDevice:
	
	def __init__(self, info):
		self.info = info
		self.Address = info["Address"]
		
	def GetProperties(self):
		return self.info
