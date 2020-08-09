from blueman.plugins.BasePlugin import BasePlugin


class ManagerPlugin(BasePlugin):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def on_unload(self):
        pass
