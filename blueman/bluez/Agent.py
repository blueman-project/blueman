# coding=utf-8
import abc

from gi.repository import Gio

from blueman.main.DbusService import DbusService, DbusError


class Agent(DbusService, metaclass=abc.ABCMeta):
    def __init__(self, agent_path):
        super().__init__(None, "org.bluez.Agent1", agent_path, Gio.BusType.SYSTEM)
        self.add_method("Release", (), "", self._on_release)
        self.add_method("RequestPinCode", ("o",), "s", self._on_request_pin_code, is_async=True)
        self.add_method("DisplayPinCode", ("o", "s"), "", self._on_display_pin_code)
        self.add_method("RequestPasskey", ("o",), "u", self._on_request_passkey, is_async=True)
        self.add_method("DisplayPasskey", ("o", "u", "y"), "", self._on_display_passkey)
        self.add_method("RequestConfirmation", ("o", "u"), "", self._on_request_confirmation, is_async=True)
        self.add_method("RequestAuthorization", ("o",), "", self._on_request_authorization, is_async=True)
        self.add_method("AuthorizeService", ("o", "s"), "", self._on_authorize_service, is_async=True)
        self.add_method("Cancel", (), "", self._on_cancel)

    @abc.abstractmethod
    def _on_release(self):
        pass

    @abc.abstractmethod
    def _on_request_pin_code(self, device_path, ok, err):
        pass

    @abc.abstractmethod
    def _on_display_pin_code(self, device_path, pin_code):
        pass

    @abc.abstractmethod
    def _on_request_passkey(self, device_path, ok, err):
        pass

    @abc.abstractmethod
    def _on_display_passkey(self, device_path, passkey, entered):
        pass

    @abc.abstractmethod
    def _on_request_confirmation(self, device_path, passkey, ok, err):
        pass

    @abc.abstractmethod
    def _on_request_authorization(self, device_path, ok, err):
        pass

    @abc.abstractmethod
    def _on_authorize_service(self, device_path, uuid, ok, err):
        pass

    @abc.abstractmethod
    def _on_cancel(self):
        pass


class BluezErrorCanceled(DbusError):
    _name = "org.bluez.Error.Canceled"


class BluezErrorRejected(DbusError):
    _name = "org.bluez.Error.Rejected"
