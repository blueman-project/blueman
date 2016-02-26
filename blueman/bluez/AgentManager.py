# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Base import Base


class AgentManager(Base):
    _interface_name = 'org.bluez.AgentManager1'

    def _init(self):
        super(AgentManager, self)._init(interface_name=self._interface_name, obj_path='/org/bluez')

    def register_agent(self, agent_path, capability='', default=False):
        self._call('RegisterAgent', agent_path, capability)
        if default:
            self._call('RequestDefaultAgent', agent_path)

    def unregister_agent(self, agent_path):
        self._call('UnregisterAgent', agent_path)
