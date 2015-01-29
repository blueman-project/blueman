class MechanismPlugin(object):
    def __init__(self, mechanism):
        self.m = mechanism
        self.timer = self.m.timer

        self.confirm_authorization = self.m.confirm_authorization

        self.on_load()

        self.m.add_definitions(self.__class__)

    def on_load(self):
        pass
