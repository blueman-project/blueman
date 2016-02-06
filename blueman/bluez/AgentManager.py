from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Base import Base
from blueman.bluez.errors import raise_dbus_error
import dbus


class AgentManager(Base):
    @raise_dbus_error
    def __init__(self):
        interface = 'org.bluez.AgentManager1'
        super(AgentManager, self).__init__(interface, '/org/bluez')

    @raise_dbus_error
    def register_agent(self, agent_path, capability='', default=False):
        self._interface.RegisterAgent(agent_path, capability)
        if default:
            self._interface.RequestDefaultAgent(agent_path)

    @raise_dbus_error
    def unregister_agent(self, agent_path):
        self._interface.UnregisterAgent(agent_path)
