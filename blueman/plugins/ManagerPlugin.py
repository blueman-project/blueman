from blueman.plugins.BasePlugin import BasePlugin


class ManagerPlugin(BasePlugin):
    # return list of (GtkMenuItem, position) tuples
    def on_request_menu_items(self, manager_menu, device):
        pass
