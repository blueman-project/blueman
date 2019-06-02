# coding=utf-8
from blueman.bluez.Base import Base
from blueman.bluez.AnyBase import AnyBase


class Device(Base):
    _interface_name = 'org.bluez.Device1'

    def __init__(self, obj_path=None):
        super().__init__(interface_name=self._interface_name, obj_path=obj_path)

    def pair(self, reply_handler=None, error_handler=None):
        self._call('Pair', reply_handler=reply_handler, error_handler=error_handler)

    def connect(self, reply_handler=None, error_handler=None):
        self._call('Connect', reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None):
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)


class AnyDevice(AnyBase):
    def __init__(self):
        super().__init__('org.bluez.Device1')
