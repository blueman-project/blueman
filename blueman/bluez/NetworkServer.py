# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase


class NetworkServer(PropertiesBase):
    _interface_name = 'org.bluez.NetworkServer1'

    def _init(self, obj_path):
        super(NetworkServer, self)._init(interface_name=self._interface_name, obj_path=obj_path)

    def register(self, uuid, bridge):
        self._call('Register', uuid, bridge)

    def unregister(self, uuid):
        self._call('Unregister', uuid)
