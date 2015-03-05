from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.BlueZInterface import BlueZInterface
from blueman.bluez.errors import raise_dbus_error
import dbus


class AgentManager(BlueZInterface):
    @raise_dbus_error
    def __init__(self):
        interface = 'org.bluez.AgentManager1'
        super(AgentManager, self).__init__(interface, '/org/bluez')

    @raise_dbus_error
    def register_agent(self, agent, capability='', default=False):
        path = agent.get_object_path()
        self.get_interface().RegisterAgent(path, capability)
        if default:
            self.get_interface().RequestDefaultAgent(path)

    @raise_dbus_error
    def unregister_agent(self, agent):
        self.get_interface().UnregisterAgent(agent.get_object_path())
