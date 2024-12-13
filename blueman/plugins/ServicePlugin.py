from typing import Literal, Union, TYPE_CHECKING


import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

if TYPE_CHECKING:
    from blueman.main.Services import BluemanServices


class ServicePlugin:
    _options: list[str]
    instances: list["ServicePlugin"] = []
    __plugin_info__: tuple[str, str]

    def __init__(self, parent: "BluemanServices"):
        ServicePlugin.instances.append(self)
        self._options = []
        self.parent = parent
        self.widget: Gtk.Grid

        self.__is_exposed = False

    # call when option has changed.
    def option_changed_notify(self, option_id: str, state: bool = True) -> None:

        if option_id not in self._options:
            self._options.append(option_id)
        else:
            if state:
                self._options.remove(option_id)

        self.parent.option_changed()

    def get_options(self) -> list[str]:
        return self._options

    def clear_options(self) -> None:
        self._options = []

    def on_load(self) -> None:
        pass

    def on_unload(self) -> None:
        pass

    # return true if apply button should be sensitive or false if not. -1 to force disabled
    def on_query_apply_state(self) -> Union[bool, Literal[-1]]:
        return False

    def on_apply(self) -> None:
        pass

    # called when current plugin's page is selected. The plugin's widget should be shown
    def on_enter(self) -> None:
        pass

    # called when current plugin's page is changed to another. The plugin's widget should be hidden.
    def on_leave(self) -> None:
        pass
