# coding=utf-8
from blueman.main.DBusServiceObject import *
import os
import struct
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.plugins.applet.KillSwitch import RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL

if not os.path.exists('/dev/rfkill'):
    raise ImportError("Hardware kill switch not found")


class RfKill(MechanismPlugin):
    @dbus_method('org.blueman.Mechanism', in_signature="b", out_signature="", invocation_keyword="invocation")
    def SetRfkillState(self, state, invocation):
        self.confirm_authorization(invocation.sender, "org.blueman.rfkill.setstate")
        f = open('/dev/rfkill', 'r+b', buffering=0)
        f.write(struct.pack("IBBBB", 0, RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL, (0 if state else 1), 0))
        f.close()
        invocation.return_value(None)
