# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Base import Base
from gi.repository import GLib

class NetworkServer(Base):
    _interface_name = 'org.bluez.NetworkServer1'

    def _init(self, obj_path):
        super(NetworkServer, self)._init(interface_name=self._interface_name, obj_path=obj_path)

    def register(self, uuid, bridge):
        param = GLib.Variant('(ss)', (uuid, bridge))
        self._call('Register', param)

    def unregister(self, uuid):
        param = GLib.Variant('(s)', (uuid,))
        self._call('Unregister', param)
