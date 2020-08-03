from typing import List, Tuple, Union, TYPE_CHECKING


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from typing_extensions import Literal

    from blueman.main.Services import BluemanServices


class ServicePlugin:
    _options: List[str]
    instances: List["ServicePlugin"] = []
    __plugin_info__: Tuple[str, str]

    def __init__(self, parent: "BluemanServices"):
        ServicePlugin.instances.append(self)
        self._options = []
        self.parent = parent

        self.__is_exposed = False
        self._is_loaded = False

    def _on_enter(self) -> None:
        if not self.__is_exposed:
            self.on_enter()
            self.__is_exposed = True

    def _on_leave(self) -> None:
        if self.__is_exposed:
            self.on_leave()
            self.__is_exposed = False

    # call when option has changed.
    def option_changed_notify(self, option_id: str, state: bool = True) -> None:

        if option_id not in self._options:
            self._options.append(option_id)
        else:
            if state:
                self._options.remove(option_id)

        self.parent.option_changed()

    def get_options(self) -> List[str]:
        return self._options

    def clear_options(self) -> None:
        self._options = []

    def on_load(self, container: Gtk.Box) -> None:
        pass

    def on_unload(self) -> None:
        pass

    # return true if apply button should be sensitive or false if not. -1 to force disabled
    def on_query_apply_state(self) -> Union[bool, "Literal[-1]"]:
        pass

    def on_apply(self) -> None:
        pass

    # called when current plugin's page is selected. The plugin's widget should be shown
    def on_enter(self) -> None:
        pass

    # called when current plugin's page is changed to another. The plugin's widget should be hidden.
    def on_leave(self) -> None:
        pass
