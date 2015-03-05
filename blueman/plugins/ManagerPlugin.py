from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.BasePlugin import BasePlugin


class ManagerPlugin(BasePlugin):
    # return list of (GtkMenuItem, position) tuples
    def on_request_menu_items(self, manager_menu, device):
        pass
