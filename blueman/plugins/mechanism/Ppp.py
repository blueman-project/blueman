from blueman.plugins.MechanismPlugin import MechanismPlugin
import os
import dbus


class Ppp(MechanismPlugin):
    def on_load(self):
        self.add_dbus_method(self.PPPConnect, in_signature="sss", out_signature="s", sender_keyword="caller",
                             async_callbacks=("ok", "err"))

    def ppp_connected(self, ppp, port, ok, err):
        ok(port)
        self.timer.resume()

    def ppp_error(self, ppp, message, ok, err):
        err(dbus.DBusException(message))
        self.timer.resume()

    def PPPConnect(self, port, number, apn, caller, ok, err):
        self.timer.stop()
        from blueman.main.PPPConnection import PPPConnection

        ppp = PPPConnection(port, number, apn)
        ppp.connect("error-occurred", self.ppp_error, ok, err)
        ppp.connect("connected", self.ppp_connected, ok, err)

        ppp.Connect()
