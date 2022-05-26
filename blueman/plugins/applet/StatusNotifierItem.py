from gettext import gettext as _

from typing import Tuple

from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.plugins.applet.StatusIcon import StatusIconImplementationProvider


class StatusNotifierItem(AppletPlugin, StatusIconImplementationProvider):
    __description__ = _("Provides a StatusNotifierItem to show a statusicon")
    __icon__ = "bluetooth-symbolic"
    __depends__ = ['StatusIcon']

    def on_query_status_icon_implementation(self) -> Tuple[str, int]:
        return "StatusNotifierItem", 20
