# coding=utf-8
from blueman.bluez.obex.Base import Base


class Session(Base):
    _interface_name = 'org.freedesktop.DBus.Properties'

    def _init(self, session_path):
        super(Session, self)._init(interface_name=self._interface_name, obj_path=session_path)

    @property
    def address(self):
        return self._call('Get', 'org.bluez.obex.Session1', 'Destination')

    @property
    def root(self):
        return self._call('Get', 'org.bluez.obex.Session1', 'Root')
