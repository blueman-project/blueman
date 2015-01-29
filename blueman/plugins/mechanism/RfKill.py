import dbus.service
from blueman.plugins.MechanismPlugin import MechanismPlugin
import os


class RfKill(MechanismPlugin):
    @dbus.service.method('org.blueman.Mechanism', in_signature="b", out_signature="")
    def SetRfkillState(self, state):
        from blueman.main.KillSwitchNG import KillSwitchNG

        k = KillSwitchNG()
        k.SetGlobalState(state)

    @dbus.service.method('org.blueman.Mechanism', in_signature="", out_signature="")
    def DevRfkillChmod(self):
        try:
            os.chmod("/dev/rfkill", 0o655)
        except:
            pass
