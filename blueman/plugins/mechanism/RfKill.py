import dbus.service
import struct
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.plugins.applet.KillSwitch import RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL


class RfKill(MechanismPlugin):
    @dbus.service.method('org.blueman.Mechanism', in_signature="b", out_signature="")
    def SetRfkillState(self, state):
        f = open('/dev/rfkill', 'w')
        f.write(struct.pack("IBBBB", 0, RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL, (0 if state else 1), 0))
        f.close()
