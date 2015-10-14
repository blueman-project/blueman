from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import dbus.service
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.BluezAgent import BluezAgent


class AuthAgent(AppletPlugin):
    __description__ = _("Provides passkey, authentication services for BlueZ daemon")
    __icon__ = "dialog-password"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]

    _agent = None
    _last_event_time = 0

    def on_load(self, applet):
        self.Applet = applet

    @dbus.service.method('org.blueman.Applet', in_signature="u")
    def SetTimeHint(self, time):
        self._last_event_time = time

    def on_unload(self):
        self._remove_agent()

    def on_manager_state_changed(self, state):
        if state:
            self._agent = BluezAgent(self.Applet.Plugins.StatusIcon, lambda: self._last_event_time)
        else:
            self._remove_agent()

    def _remove_agent(self):
        if self._agent:
            self._agent.Release()
            del self._agent
