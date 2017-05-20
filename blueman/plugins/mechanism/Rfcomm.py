# coding=utf-8
import dbus.service
import os
import subprocess
import signal
from blueman.Constants import RFCOMM_WATCHER_PATH
from blueman.plugins.MechanismPlugin import MechanismPlugin


class Rfcomm(MechanismPlugin):
    files = {}

    @dbus.service.method('org.blueman.Mechanism', in_signature="d")
    def open_rfcomm(self, port_id):
        subprocess.Popen([RFCOMM_WATCHER_PATH, '/dev/rfcomm%d' % port_id])

    @dbus.service.method('org.blueman.Mechanism', in_signature="d")
    def close_rfcomm(self, port_id):
        command = 'blueman-rfcomm-watcher /dev/rfcomm%d' % port_id

        out, err = subprocess.Popen(['ps', '-e', 'o', 'pid,args'], stdout=subprocess.PIPE).communicate()
        for line in out.decode("UTF-8").splitlines():
            if command in line:
                os.kill(int(line.split(None, 1)[0]), signal.SIGTERM)
