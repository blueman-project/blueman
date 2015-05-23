from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.Functions import dprint
from blueman.bluez.obex.Base import Base


class AgentManager(Base):
    def __init__(self):
        super(AgentManager, self).__init__('org.bluez.obex.AgentManager1', '/org/bluez/obex')

    def register_agent(self, agent_path):
        def on_registered():
            dprint(agent_path)

        def on_register_failed(error):
            dprint(agent_path, error)

        self._call('RegisterAgent', agent_path, reply_handler=on_registered, error_handler=on_register_failed)

    def unregister_agent(self, agent_path):
        def on_unregistered():
            dprint(agent_path)

        def on_unregister_failed(error):
            dprint(agent_path, error)

        self._call('UnregisterAgent', agent_path, reply_handler=on_unregistered, error_handler=on_unregister_failed)
