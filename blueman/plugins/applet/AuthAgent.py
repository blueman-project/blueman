from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus.service
from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
import blueman.main.applet.BluezAgent as BluezAgent
import blueman.bluez as Bluez

from gi.repository import GObject
from gi.repository import Gtk


class AuthAgent(AppletPlugin):
    __description__ = _("Provides passkey, authentication services for BlueZ daemon")
    __icon__ = "dialog-password"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]

    def on_load(self, applet):
        self.Applet = applet

        self.agents = []
        self.last_event_time = 0

        self.agent_manager = Bluez.AgentManager()

    @dbus.service.method('org.blueman.Applet', in_signature="u")
    def SetTimeHint(self, time):
        self.last_event_time = time

    def on_unload(self):
        for agent in self.agents:
            if self.legacy():
                agent.adapter.unregister_agent(agent)
            else:
                self.agent_manager.unregister_agent(agent)
            agent.Release()

    def on_manager_state_changed(self, state):
        if state:
            adapters = self.Applet.Manager.list_adapters()
            for adapter in adapters:
                self.register_agent(adapter)

        else:
            for agent in self.agents:
                agent.Release()

    def on_adapter_added(self, path):
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
            if self.legacy():
                agent = BluezAgent.AdapterAgent(self.Applet.Plugins.StatusIcon, adapter, self.get_event_time)
                agent.signal = agent.connect("released", self.on_released)
                adapter.register_agent(agent, "KeyboardDisplay")
                self.agents.append(agent)
            elif not self.agents:
                agent = BluezAgent.GlobalAgent(self.Applet.Plugins.StatusIcon, self.get_event_time)
                self.agent_manager.register_agent(agent, "KeyboardDisplay", default=True)
                self.agents.append(agent)

        except Exception as e:
            dprint("Failed to register agent")
            dprint(e)

    def legacy(self):
        return self.Applet.Manager.get_interface_version()[0] < 5
