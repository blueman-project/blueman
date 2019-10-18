# coding=utf-8
from typing import Optional

from blueman.Sdp import ServiceUUID
from blueman.bluez.Device import Device


class Service(object):
    __svclass_id__: int
    __description__ = None
    __icon__: str
    __priority__: int

    def __init__(self, device: Device, uuid: str):
        self.__device = device
        self.__uuid = uuid

    @property
    def name(self) -> str:
        return ServiceUUID(self.__uuid).name

    @property
    def device(self) -> Device:
        return self.__device

    @property
    def uuid(self) -> str:
        return self.__uuid

    @property
    def short_uuid(self) -> Optional[int]:
        return ServiceUUID(self.__uuid).short_uuid

    @property
    def description(self) -> Optional[str]:
        return self.__description__

    @property
    def icon(self) -> str:
        return self.__icon__

    @property
    def priority(self) -> int:
        return self.__priority__
