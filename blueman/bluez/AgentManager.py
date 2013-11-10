from BlueZInterface import BlueZInterface
from errors import raise_dbus_error
import dbus


class AgentManager(BlueZInterface):
    @raise_dbus_error
    def __init__(self):
        interface = 'org.bluez.AgentManager1'
        super(AgentManager, self).__init__(interface, '/')

    @raise_dbus_error
    def register_agent(self, agent, capability=''):
        self.get_interface().RegisterAgent(agent.get_object_path(), capability)

    @raise_dbus_error
    def unregister_agent(self, agent):
        self.get_interface().UnregisterAgent(agent.get_object_path())
