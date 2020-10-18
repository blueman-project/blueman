from abc import ABC, abstractmethod
from typing import Optional, Callable, List, Set, Collection

from blueman.Sdp import ServiceUUID
from blueman.bluez.Device import Device


class Instance:
    def __init__(self, name: str, port: int = 0) -> None:
        self.name = name
        self.port = port


class Action:
    def __init__(self, title: str, icon: str, plugins: Collection[str], callback: Callable[[], None]) -> None:
        self.title = title
        self.icon = icon
        self.plugins = plugins
        self.callback = callback

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Action) and self.title == other.title

    def __hash__(self) -> int:
        return hash(self.title)


class Service(ABC):
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

    @property
    @abstractmethod
    def available(self) -> bool:
        ...

    @property
    @abstractmethod
    def connectable(self) -> bool:
        ...

    @property
    @abstractmethod
    def connected_instances(self) -> List[Instance]:
        ...

    @property
    def common_actions(self) -> Set[Action]:
        return set()
