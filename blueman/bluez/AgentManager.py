# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.bluez.Base import Base
from gi.repository import GLib

class AgentManager(Base):
    _interface_name = 'org.bluez.AgentManager1'

    def _init(self):
        super(AgentManager, self)._init(interface_name=self._interface_name, obj_path='/org/bluez')

    def register_agent(self, agent_path, capability='', default=False):
        param = GLib.Variant('(os)', (agent_path, capability))
        self._call('RegisterAgent', param)
        if default:
            default_param = GLib.Variant('(o)', (agent_path,))
            self._call('RequestDefaultAgent', default_param)

    def unregister_agent(self, agent_path):
        param = GLib.Variant('(o)', (agent_path,))
        self._call('UnregisterAgent', param)
