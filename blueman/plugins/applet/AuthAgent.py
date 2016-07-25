# coding=utf-8
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.main.DBusServiceObject import *
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

    @dbus_method('org.blueman.Applet', in_signature="u")
    def SetTimeHint(self, time):
        self._last_event_time = time

    def on_unload(self):
        if self._agent:
            self._agent.unregister_agent()
            self._agent = None

    def on_manager_state_changed(self, state):
        if state:
            self._agent = BluezAgent(self.Applet.Plugins.StatusIcon, lambda: self._last_event_time)
            self._agent.register_agent()
        else:
            # At this point bluez already called Release on the agent
            self._agent = None
