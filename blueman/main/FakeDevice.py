

class FakeDevice:
	
	def __init__(self, info):
		self.info = info
		self.Address = info["Address"]
		#info["Connected"] = False
		self.Fake = True
		self.UUIDs = []
		
	def GetProperties(self):
		return self.info
