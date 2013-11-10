class FakeDevice:
    def __init__(self, info):
        self.info = info
        self.Address = info["Address"]
        self.Fake = True
        self.UUIDs = []

    def get_properties(self):
        return self.info
