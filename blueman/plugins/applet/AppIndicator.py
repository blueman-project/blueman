# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin

# Check if Appindicator is available and raise ImportError
from gi import require_version
try:
    require_version('AppIndicator3', '0.1')
except ValueError:
    raise ImportError("AppIndicator3 not found")


class AppIndicator(AppletPlugin):
    __description__ = _("Uses libappindicator to show a statusicon")
    __icon__ = "blueman-tray"
    __author__ = "Walmis"
    __depends__ = ['StatusIcon']

    def on_query_status_icon_implementation(self):
        return 'AppIndicator'
