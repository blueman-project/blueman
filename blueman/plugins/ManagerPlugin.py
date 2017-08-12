# coding=utf-8
from blueman.plugins.BasePlugin import BasePlugin


class ManagerPlugin(BasePlugin):
    def __init__(self, parent):
        super().__init__(parent)

    def on_unload(self):
        pass

    # return list of (GtkMenuItem, position) tuples
    def on_request_menu_items(self, manager_menu, device):
        pass
