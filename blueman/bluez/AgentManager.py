from blueman.bluez.Base import Base
from gi.repository import GLib


class AgentManager(Base):
    _interface_name = 'org.bluez.AgentManager1'
    _obj_path = '/org/bluez'

    def __init__(self) -> None:
        super().__init__(obj_path=self._obj_path)

    def register_agent(self, agent_path: str, capability: str = "", default: bool = False) -> None:
        param = GLib.Variant('(os)', (agent_path, capability))
        self._call('RegisterAgent', param)
        if default:
            default_param = GLib.Variant('(o)', (agent_path,))
            self._call('RequestDefaultAgent', default_param)

    def unregister_agent(self, agent_path: str) -> None:
        param = GLib.Variant('(o)', (agent_path,))
        self._call('UnregisterAgent', param)
