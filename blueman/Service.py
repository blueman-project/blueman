# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Sdp import ServiceUUID


class Service(object):
    __group__ = None
    __svclass_id__ = None
    __description__ = None
    __icon__ = None
    __priority__ = None

    def __init__(self, device, uuid):
        self.__device = device
        self.__uuid = uuid

    @property
    def name(self):
        return ServiceUUID(self.__uuid).name

    @property
    def device(self):
        return self.__device

    @property
    def uuid(self):
        return self.__uuid

    def short_uuid(self):
        return ServiceUUID(self.__uuid).short_uuid

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
        return self.__device['Connected']

    def connect(self, reply_handler=None, error_handler=None):
        self.__device.connect(reply_handler=reply_handler, error_handler=error_handler)

    def disconnect(self, reply_handler=None, error_handler=None, *args):
        self.__device.disconnect(reply_handler=reply_handler, error_handler=error_handler)
