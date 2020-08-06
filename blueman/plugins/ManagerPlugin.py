from blueman.plugins.BasePlugin import BasePlugin


class ManagerPlugin(BasePlugin):
    def __init__(self, parent):
        super().__init__(parent)

    def on_unload(self):
        pass
