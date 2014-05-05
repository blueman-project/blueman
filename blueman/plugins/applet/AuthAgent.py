from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
import blueman.main.applet.BluezAgent as BluezAgent
import blueman.bluez as Bluez

from gi.repository import GObject
from gi.repository import Gtk


class AuthAgent(AppletPlugin):
    __description__ = _("Provides passkey, authentication services for BlueZ daemon")
    __icon__ = "gtk-dialog-authentication"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]

    def on_load(self, applet):
        self.Applet = applet
        self.add_dbus_method(self.SetTimeHint, in_signature="u")

        self.last_event_time = 0

<<<<<<< HEAD
        self.agent_manager = Bluez.AgentManager()
=======
        self.legacy = self.Applet.Manager.get_interface_version()[0] < 5

        if self.legacy:
            self.agents = []
        else:
            self.agent_manager = Bluez.AgentManager()
            self.agent = BluezAgent.GlobalAgent(self.Applet.Plugins.StatusIcon, self.get_event_time)
            self.agent_manager.register_agent(self.agent, "DisplayYesNo")
>>>>>>> (WIP!) Replace bluez layer

    def SetTimeHint(self, time):
        self.last_event_time = time

    def on_unload(self):
<<<<<<< HEAD
        for agent in self.agents:
            if self.legacy():
                agent.adapter.unregister_agent(agent)
            else:
                self.agent_manager.unregister_agent(agent)
=======
        if self.legacy:
            for agent in self.agents:
                agent.adapter.unregister_agent(agent)
        else:
            self.agent_manager.unregister_agent(self.agent)
>>>>>>> (WIP!) Replace bluez layer

    def on_manager_state_changed(self, state):
        if not self.legacy:
            return

        if state:
            adapters = self.Applet.Manager.list_adapters()
            for adapter in adapters:
                self.register_agent(adapter)
        else:
            for agent in self.agents:
                agent.Release()

    def on_adapter_added(self, path):
        if not self.legacy:
            return

        adapter = Bluez.Adapter(path)
        self.register_agent(adapter)

    def on_released(self, agent):
        agent.disconnect(agent.signal)
        self.agents.remove(agent)

    def get_event_time(self):
        return self.last_event_time

    def register_agent(self, adapter):
        dprint("Registering agent")
        try:
<<<<<<< HEAD
            if self.legacy():
                agent = BluezAgent.AdapterAgent(self.Applet.Plugins.StatusIcon, adapter, self.get_event_time)
                agent.signal = agent.connect("released", self.on_released)
                adapter.register_agent(agent, "DisplayYesNo")
                self.agents.append(agent)
            elif not self.agents:
                agent = BluezAgent.GlobalAgent(self.Applet.Plugins.StatusIcon, self.get_event_time)
                self.agent_manager.register_agent(agent, "DisplayYesNo", default=True)
                self.agents.append(agent)
=======
            agent = BluezAgent.AdapterAgent(self.Applet.Plugins.StatusIcon, adapter, self.get_event_time)
            agent.signal = agent.connect("released", self.on_released)
            adapter.register_agent(agent, "DisplayYesNo")
            self.agents.append(agent)
>>>>>>> (WIP!) Replace bluez layer

        except Exception as e:
            dprint("Failed to register agent")
            dprint(e)

    def legacy(self):
        return self.Applet.Manager.get_interface_version()[0] < 5
