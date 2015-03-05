from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
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
        self.timer.stop()
        from blueman.main.PPPConnection import PPPConnection

        ppp = PPPConnection(port, number, apn)
        ppp.connect("error-occurred", self.ppp_error, ok, err)
        ppp.connect("connected", self.ppp_connected, ok, err)

        ppp.Connect()
