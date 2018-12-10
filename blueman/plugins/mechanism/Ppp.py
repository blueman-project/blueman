from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
import signal
import subprocess
import dbus
import dbus.service


class Ppp(MechanismPlugin):
    def ppp_connected(self, ppp, port, ok, err):
        ok(port)
        self.timer.resume()

    def ppp_error(self, ppp, message, ok, err):
        err(dbus.DBusException(message))
        self.timer.resume()

    @dbus.service.method('org.blueman.Mechanism', in_signature="sss", out_signature="s", sender_keyword="caller",
                         async_callbacks=("ok", "err"))
    def PPPConnect(self, port, number, apn, caller, ok, err):
        self.confirm_authorization(caller, "org.blueman.pppd.pppconnect")
        self.timer.stop()
        from blueman.main.PPPConnection import PPPConnection

        ppp = PPPConnection(port, number, apn)
        ppp.connect("error-occurred", self.ppp_error, ok, err)
        ppp.connect("connected", self.ppp_connected, ok, err)

        ppp.Connect()

    @dbus.service.method('org.blueman.Mechanism', in_signature="i", out_signature="s", sender_keyword="caller")
    def PPPDisconnect(self, port, caller):
        self.confirm_authorization(caller, "org.blueman.pppd.pppconnect")
        p = subprocess.Popen(['ps', '-e', 'o', 'pid,args'], stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise dbus.DBusException('Failed to retrieve list of process ids')

        pid = None
        for line in stdout.decode('utf-8').splitlines():
            if '/usr/sbin/pppd /dev/rfcomm%s' % port in line:
                pid = int(line.split(None, 1)[0])

        if pid is None:
            raise dbus.DBusException('No proces id found for pppd')
        else:
            os.kill(pid, signal.SIGTERM)
            return 'Succesfully killed pppd with pid %s' % pid
