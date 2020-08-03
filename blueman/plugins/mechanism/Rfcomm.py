import os
import subprocess
import signal
from blueman.Constants import RFCOMM_WATCHER_PATH
from blueman.plugins.MechanismPlugin import MechanismPlugin


class Rfcomm(MechanismPlugin):
    def on_load(self) -> None:
        self.parent.add_method("OpenRFCOMM", ("d",), "", self._open_rfcomm)
        self.parent.add_method("CloseRFCOMM", ("d",), "", self._close_rfcomm)

    def _open_rfcomm(self, port_id: int) -> None:
        subprocess.Popen([RFCOMM_WATCHER_PATH, '/dev/rfcomm%d' % port_id])

    def _close_rfcomm(self, port_id: int) -> None:
        command = 'blueman-rfcomm-watcher /dev/rfcomm%d' % port_id

        out, err = subprocess.Popen(['ps', '-e', 'o', 'pid,args'], stdout=subprocess.PIPE).communicate()
        for line in out.decode("UTF-8").splitlines():
            pid, cmdline = line.split(maxsplit=1)
            if command in cmdline:
                os.kill(int(pid), signal.SIGTERM)
