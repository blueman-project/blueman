from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus
from blueman.Sdp import uuid128_to_uuid16, uuid16_to_name
from blueman.bluez.BlueZInterface import BlueZInterface


class Service(object):
    __group__ = None
    __svclass_id__ = None
    __description__ = None
    __icon__ = None
    __priority__ = None

    _legacy_interface = None

    def __init__(self, device, uuid, init_legacy_interface=True):
        self.__device = device
        self.__uuid = uuid
        if init_legacy_interface and BlueZInterface.get_interface_version()[0] < 5:
            bus = dbus.SystemBus()
            proxy = bus.get_object("org.bluez", self.__device.get_object_path())
            self._legacy_interface = dbus.Interface(proxy, 'org.bluez.%s' % self.__class__.__name__)

    @property
    def name(self):
        return uuid16_to_name(uuid128_to_uuid16(self.__uuid))

    @property
    def device(self):
        return self.__device

    @property
    def uuid(self):
        return self.__uuid

    @property
    def description(self):
        return self.__description__

    @property
    def icon(self):
        return self.__icon__

    @property
    def priority(self):
        return self.__priority__

    @property
    def group(self):
        return self.__group__

    @property
    def connected(self):
        if self._legacy_interface:
            return self._legacy_interface.GetProperties()['Connected']
        else:
            return self.__device.Device.get_properties()['Connected']

    def connect(self, reply_handler=None, error_handler=None):
        if self._legacy_interface:
            self._legacy_interface.Connect(self.__uuid, reply_handler=reply_handler, error_handler=error_handler)
        else:
            self.__device.Device.connect(reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None, *args):
        if self._legacy_interface:
            self._legacy_interface.Disconnect(self.__uuid, reply_handler=reply_handler, error_handler=error_handler)
        else:
            self.__device.Device.disconnect(reply_handler=reply_handler, error_handler=error_handler)
