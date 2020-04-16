import logging

from blueman.bluez.errors import BluezDBusException
from blueman.bluez.obex.Base import Base
from gi.repository import GLib


class AgentManager(Base):
    _interface_name = 'org.bluez.obex.AgentManager1'
    _obj_path = '/org/bluez/obex'

    def __init__(self) -> None:
        super().__init__(obj_path=self._obj_path)

    def register_agent(self, agent_path: str) -> None:
        def on_registered() -> None:
            logging.info(agent_path)

        def on_register_failed(error: BluezDBusException) -> None:
            logging.error(f"{agent_path} {error}")

        param = GLib.Variant('(o)', (agent_path,))
        self._call('RegisterAgent', param, reply_handler=on_registered, error_handler=on_register_failed)

    def unregister_agent(self, agent_path: str) -> None:
        def on_unregistered() -> None:
            logging.info(agent_path)

        def on_unregister_failed(error: BluezDBusException) -> None:
            logging.error(f"{agent_path} {error}")

        param = GLib.Variant('(o)', (agent_path,))
        self._call('UnregisterAgent', param, reply_handler=on_unregistered, error_handler=on_unregister_failed)
