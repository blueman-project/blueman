from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from blueman.main.MechanismApplication import MechanismApplication


class MechanismPlugin:
    def __init__(self, parent: "MechanismApplication"):
        self.parent = parent
        self.timer = self.parent.timer

        self.confirm_authorization = self.parent.confirm_authorization

        self.on_load()

    def on_load(self) -> None:
        pass
