# coding=utf-8


class MechanismPlugin(object):
    def __init__(self, parent):
        self.parent = parent
        self.timer = self.parent.timer

        self.confirm_authorization = self.parent.confirm_authorization

        self.on_load()

    def on_load(self):
        pass
