# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.PropertiesBase import PropertiesBase
from blueman.bluez.AnyBase import AnyBase
from gi.repository import GLib


class Network(PropertiesBase):
    _interface_name = 'org.bluez.Network1'

    def _init(self, obj_path=None):
        super(Network, self)._init(interface_name=self._interface_name, obj_path=obj_path)

    def connect(self, uuid, reply_handler=None, error_handler=None):
        self._call('Connect', uuid, reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None):
        self._call('Disconnect', reply_handler=reply_handler, error_handler=error_handler)

class AnyNetwork(AnyBase):
    def __init__(self):
        super(AnyNetwork, self).__init__('org.bluez.Network1')
