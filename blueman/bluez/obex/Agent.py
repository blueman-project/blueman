# coding=utf-8
import abc

from gi.repository import Gio

from blueman.main.DbusService import DbusService, DbusError


class Agent(DbusService, metaclass=abc.ABCMeta):
    def __init__(self, agent_path):
        super().__init__(None, "org.bluez.obex.Agent1", agent_path, Gio.BusType.SESSION)
        self.add_method("Release", (), "", self._release)
        self.add_method("Cancel", (), "", self._cancel)
        self.add_method("AuthorizePush", ("o",), "s", self._authorize_push, is_async=True)
        self.register()

    @abc.abstractmethod
    def _release(self):
        pass

    @abc.abstractmethod
    def _cancel(self):
        pass

    @abc.abstractmethod
    def _authorize_push(self, transfer_path, ok, err):
        pass


class ObexErrorRejected(DbusError):
    _name = "org.bluez.obex.Error.Rejected"


class ObexErrorCanceled(DbusError):
    _name = "org.bluez.obex.Error.Canceled"
