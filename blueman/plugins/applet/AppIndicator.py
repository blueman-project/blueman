# coding=utf-8
from blueman.plugins.AppletPlugin import AppletPlugin

import gi
try:
    gi.require_version('AppIndicator3', '0.1')
    from gi.repository import AppIndicator3 as girAppIndicator
except ValueError:
    raise ImportError


class AppIndicator(AppletPlugin):
    __description__ = _("Uses libappindicator to show a statusicon")
    __icon__ = "blueman-tray"
    __author__ = "Walmis"
    __depends__ = ['StatusIcon']

    def on_query_status_icon_implementation(self):
        return 'AppIndicator'
