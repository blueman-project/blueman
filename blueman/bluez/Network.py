# coding=utf-8
from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase
from gi.repository import GLib


class Network(Base):
    _interface_name = 'org.bluez.Network1'

    def __init__(self, obj_path=None):
        super().__init__(interface_name=self._interface_name, obj_path=obj_path)

    def connect(self, uuid, reply_handler=None, error_handler=None):
        param = GLib.Variant('(s)', (uuid,))
        self._call('Connect', param, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None):
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)


class AnyNetwork(AnyBase):
    def __init__(self):
        super().__init__('org.bluez.Network1')
