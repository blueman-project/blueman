from typing import Callable

from blueman.main.PPPConnection import PPPConnection
from blueman.plugins.MechanismPlugin import MechanismPlugin


class Ppp(MechanismPlugin):
    def on_load(self) -> None:
        self.parent.add_method("PPPConnect", ("s", "s", "s"), "s", self._ppp_connect, pass_sender=True, is_async=True)

    def _ppp_connected(self, _ppp: PPPConnection, port: str, ok: Callable[[str], None]) -> None:
        ok(port)
        self.timer.resume()

    def _ppp_error(self, _ppp: PPPConnection, message: str, err: Callable[[str], None]) -> None:
        err(message)
        self.timer.resume()

    def _ppp_connect(self, port: str, number: str, apn: str, caller: str,
                     ok: Callable[[str], None], err: Callable[[str], None]) -> None:
        self.confirm_authorization(caller, "org.blueman.pppd.pppconnect")
        self.timer.stop()

        ppp = PPPConnection(port, number, apn)
        ppp.connect("error-occurred", self._ppp_error, err)
        ppp.connect("connected", self._ppp_connected, ok)

        ppp.connect_rfcomm()
