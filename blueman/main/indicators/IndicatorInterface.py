from abc import abstractmethod, ABCMeta
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from blueman.plugins.applet.Menu import MenuItemDict


class IndicatorNotAvailable(RuntimeError):
    pass


class IndicatorInterface(metaclass=ABCMeta):
    @abstractmethod
    def set_icon(self, icon_name: str) -> None:
        ...

    @abstractmethod
    def set_tooltip_title(self, title: str) -> None:
        ...

    @abstractmethod
    def set_tooltip_text(self, text: str) -> None:
        ...

    @abstractmethod
    def set_visibility(self, visible: bool) -> None:
        ...

    @abstractmethod
    def set_menu(self, menu: Iterable["MenuItemDict"]) -> None:
        ...
