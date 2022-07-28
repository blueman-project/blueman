from typing import TYPE_CHECKING

from blueman.plugins.BasePlugin import BasePlugin

if TYPE_CHECKING:
    from blueman.config.Settings import BluemanSettings
    from blueman.main.Manager import Blueman


class ManagerPlugin(BasePlugin):
    def __init__(self, parent: "Blueman", settings: "BluemanSettings"):
        super().__init__()
        self.parent = parent
        self.settings = settings

    def on_unload(self) -> None:
        pass
