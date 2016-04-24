from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus.service
import os
import struct
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.plugins.applet.KillSwitch import RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL

if not os.path.exists('/dev/rfkill'):
    raise ImportError("Hardware kill switch not found")

class RfKill(MechanismPlugin):
    @dbus.service.method('org.blueman.Mechanism', in_signature="b", out_signature="", sender_keyword="caller")
    def SetRfkillState(self, state, caller):
        self.confirm_authorization(caller, "org.blueman.rfkill.setstate")
        f = open('/dev/rfkill', 'r+b', buffering=0)
        f.write(struct.pack("IBBBB", 0, RFKILL_TYPE_BLUETOOTH, RFKILL_OP_CHANGE_ALL, (0 if state else 1), 0))
        f.close()
