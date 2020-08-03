from typing import TYPE_CHECKING

from blueman.plugins.BasePlugin import BasePlugin

if TYPE_CHECKING:
    from blueman.main.Manager import Blueman


class ManagerPlugin(BasePlugin):
    def __init__(self, parent: "Blueman"):
        super().__init__()
        self.parent = parent

    def on_unload(self) -> None:
        pass
