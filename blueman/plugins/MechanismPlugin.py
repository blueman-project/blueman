class MechanismPlugin(object):
    def __init__(self, mechanism):
        self.m = mechanism
        self.timer = self.m.timer

        self.confirm_authorization = self.m.confirm_authorization

        self.on_load()

    def add_dbus_method(self, func, *args, **kwargs):
        self.m.add_method(func, *args, **kwargs)

    def add_dbus_signal(self, func, *args, **kwargs):
        self.m.add_signal(func, *args, **kwargs)

    def check_auth(self, id, caller):
        self.m.confirm_authorization(id, caller)

    def on_load(self):
        pass
