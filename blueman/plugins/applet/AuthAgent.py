from gettext import gettext as _

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.BluezAgent import BluezAgent


class AuthAgent(AppletPlugin):
    __description__ = _("Provides passkey, authentication services for BlueZ daemon")
    __icon__ = "blueman-pair-symbolic"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon"]

    _agent = None

    def on_unload(self) -> None:
        if self._agent:
            self._agent.unregister_agent()
            self._agent = None

    def on_manager_state_changed(self, state: bool) -> None:
        if state:
            self._agent = BluezAgent()
            self._agent.register_agent()
        else:
            # At this point bluez already called Release on the agent
            self._agent = None
