# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.MechanismPlugin import MechanismPlugin
from blueman.main.DBusServiceObject import *
from gi.repository import GLib


class Ppp(MechanismPlugin):
    def ppp_connected(self, ppp, port):
        self.timer.resume()
        return(port)

    def ppp_error(self, ppp, message):
        self.timer.resume()
        raise(GLib.Error(message))

    @dbus_method('org.blueman.Mechanism', in_signature="sss", out_signature="s", sender="caller")
    def PPPConnect(self, port, number, apn, caller):
        self.confirm_authorization(caller, "org.blueman.pppd.pppconnect")
        self.timer.stop()
        from blueman.main.PPPConnection import PPPConnection

        ppp = PPPConnection(port, number, apn)
        ppp.connect("error-occurred", self.ppp_error)
        ppp.connect("connected", self.ppp_connected)

        ppp.Connect()
