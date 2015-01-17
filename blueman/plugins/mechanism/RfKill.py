from blueman.plugins.MechanismPlugin import MechanismPlugin
import os


class RfKill(MechanismPlugin):
    def on_load(self):
        self.add_dbus_method(self.SetRfkillState, in_signature="b", out_signature="")
        self.add_dbus_method(self.DevRfkillChmod, in_signature="", out_signature="")

    def SetRfkillState(self, state):
        from blueman.main.KillSwitchNG import KillSwitchNG

        k = KillSwitchNG()
        k.SetGlobalState(state)

    def DevRfkillChmod(self):
        try:
            os.chmod("/dev/rfkill", 0655)
        except:
            pass
