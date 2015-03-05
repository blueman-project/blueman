from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

class FakeDevice:
    def __init__(self, info):
        self.info = info
        self.Address = info["Address"]
        self.Fake = True
        self.UUIDs = []

    def get_properties(self):
        return self.info
