from blueman.Functions import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.BluezAgent import AdapterAgent
import blueman.bluez as Bluez

import gobject
import gtk


class AuthAgent(AppletPlugin):
    __description__ = _("Provides passkey, authentication services for BlueZ daemon")
    __icon__ = "gtk-dialog-authentication"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]

    def on_load(self, applet):
        self.Applet = applet
        self.add_dbus_method(self.SetTimeHint, in_signature="u")

        self.agents = []
        self.last_event_time = 0

    def SetTimeHint(self, time):
        self.last_event_time = time

    def on_unload(self):
        for agent in self.agents:
            agent.adapter.UnregisterAgent(agent)

    def on_manager_state_changed(self, state):
        if state:
            adapters = self.Applet.Manager.ListAdapters()
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
            agent = AdapterAgent(self.Applet.Plugins.StatusIcon, adapter, self.get_event_time)
            agent.signal = agent.connect("released", self.on_released)
            adapter.RegisterAgent(agent, "DisplayYesNo")
            self.agents.append(agent)

        except Exception as e:
            dprint("Failed to register agent")
            dprint(e)
