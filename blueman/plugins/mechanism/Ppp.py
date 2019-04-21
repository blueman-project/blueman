# coding=utf-8

from blueman.plugins.MechanismPlugin import MechanismPlugin


class Ppp(MechanismPlugin):
    def on_load(self):
        self.parent.add_method("PPPConnect", ("s", "s", "s"), "s", self._ppp_connect, pass_sender=True, is_async=True)

    def _ppp_connected(self, _ppp, port, ok):
        ok(port)
        self.timer.resume()

    def _ppp_error(self, _ppp, message, err):
        err(message)
        self.timer.resume()

    def _ppp_connect(self, port, number, apn, caller, ok, err):
        self.confirm_authorization(caller, "org.blueman.pppd.pppconnect")
        self.timer.stop()
        from blueman.main.PPPConnection import PPPConnection

        ppp = PPPConnection(port, number, apn)
        ppp.connect("error-occurred", self._ppp_error, err)
        ppp.connect("connected", self._ppp_connected, ok)

        ppp.connect_rfcomm()
