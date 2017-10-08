# coding=utf-8
import logging
from blueman.bluez.obex.Base import Base
from gi.repository import GLib


class AgentManager(Base):
    _interface_name = 'org.bluez.obex.AgentManager1'

    def __init__(self):
        super().__init__(interface_name=self._interface_name, obj_path='/org/bluez/obex')

    def register_agent(self, agent_path):
        def on_registered():
            logging.info(agent_path)

        def on_register_failed(error):
            logging.error("%s %s" % (agent_path, error))

        param = GLib.Variant('(o)', (agent_path,))
        self._call('RegisterAgent', param, reply_handler=on_registered, error_handler=on_register_failed)

    def unregister_agent(self, agent_path):
        def on_unregistered():
            logging.info(agent_path)

        def on_unregister_failed(error):
            logging.error("%s %s" % (agent_path, error))

        param = GLib.Variant('(o)', (agent_path,))
        self._call('UnregisterAgent', param, reply_handler=on_unregistered, error_handler=on_unregister_failed)
