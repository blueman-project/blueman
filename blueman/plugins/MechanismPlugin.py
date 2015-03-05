from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

class MechanismPlugin(object):
    def __init__(self, mechanism):
        self.m = mechanism
        self.timer = self.m.timer

        self.confirm_authorization = self.m.confirm_authorization

        self.on_load()

        self.m.add_definitions(self)

    def on_load(self):
        pass
