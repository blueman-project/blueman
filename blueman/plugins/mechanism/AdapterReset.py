import logging

from blueman.main.AdapterReset import AdapterResetError, reset_controller
from blueman.main.DbusService import DbusError
from blueman.plugins.MechanismPlugin import MechanismPlugin


class AdapterResetFailed(DbusError):
    _name = "org.blueman.Error.AdapterResetFailed"


class AdapterReset(MechanismPlugin):
    def on_load(self) -> None:
        self.parent.add_method("ResetAdapter", ("s",), ("s",), self._reset_adapter, pass_sender=True)

    def _reset_adapter(self, hci: str, caller: str) -> str:
        self.confirm_authorization(caller, "org.blueman.adapter.reset")
        self.timer.stop()
        try:
            method = reset_controller(hci)
        except AdapterResetError as e:
            raise AdapterResetFailed(str(e)) from e
        finally:
            self.timer.resume()
        logging.info(f"Reset {hci} by {method}")
        return method
