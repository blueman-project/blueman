# coding=utf-8
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

    @property
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
