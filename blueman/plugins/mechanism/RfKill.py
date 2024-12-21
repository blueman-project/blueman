import pathlib
import struct
from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.plugins.applet.KillSwitch import RFKILL_TYPE_BLUETOOTH, RFKillOp

if not pathlib.Path('/dev/rfkill').exists():
    raise ImportError("Hardware kill switch not found")


class RfKill(MechanismPlugin):
    def on_load(self) -> None:
        self.parent.add_method("SetRfkillState", ("b",), "", self._set_rfkill_state, pass_sender=True)

    def _set_rfkill_state(self, state: bool, caller: str) -> None:
        self.confirm_authorization(caller, "org.blueman.rfkill.setstate")
        with open('/dev/rfkill', 'r+b', buffering=0) as f:
            f.write(struct.pack("IBBBB", 0, RFKILL_TYPE_BLUETOOTH, RFKillOp.CHANGE_ALL, (0 if state else 1), 0))
