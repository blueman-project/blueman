# coding=utf-8
from blueman.bluez.obex.Base import Base
from gi.repository import GLib


class Session(Base):
    _interface_name = 'org.freedesktop.DBus.Properties'

    def _init(self, session_path):
        super(Session, self)._init(interface_name=self._interface_name, obj_path=session_path)

    @property
    def address(self):
        param = GLib.Variant('(ss)', ('org.bluez.obex.Session1', 'Destination'))
        return self._call('Get', param)

    @property
    def root(self):
        param = GLib.Variant('(ss)', ('org.bluez.obex.Session1', 'Root'))
        return self._call('Get', param)
