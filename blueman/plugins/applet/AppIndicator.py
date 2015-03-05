from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

from blueman.plugins.AppletPlugin import AppletPlugin

from gi.repository import AppIndicator3 as girAppIndicator


class AppIndicator(AppletPlugin):
    __description__ = _("Uses libappindicator to show a statusicon")
    __icon__ = "blueman-tray"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon", "Menu"]
    
    def on_load(self, applet):
        
        self.indicator = girAppIndicator.Indicator.new ("blueman",
                                                        self.Applet.Plugins.StatusIcon.props.icon_name,
                                                        girAppIndicator.IndicatorCategory.APPLICATION_STATUS)
        
        self.indicator.set_status(girAppIndicator.IndicatorStatus.ACTIVE)
        
        self.indicator.set_menu(applet.Plugins.Menu.get_menu())
        
        self.s =  self.Applet.Plugins.StatusIcon.connect("notify::icon-name", self.on_notify)

        self.override_method(self.Applet.Plugins.StatusIcon, "set_visible", self.set_visible)
        
        self.Applet.Plugins.StatusIcon.props.visible = False

    def set_visible(self, _, visible):
        if visible:
            self.indicator.set_status(girAppIndicator.IndicatorStatus.ACTIVE)
        else:
            self.indicator.set_status(girAppIndicator.IndicatorStatus.PASSIVE)
        
    def on_notify(self, *args):
        self.update_icon()
        
    def on_unload(self):
        del self.indicator
        self.Applet.Plugins.StatusIcon.QueryVisibility()
        self.Applet.Plugins.StatusIcon.disconnect(self.s)
        
    def update_icon(self):
        self.indicator.set_icon(self.Applet.Plugins.StatusIcon.props.icon_name)
        self.indicator.set_status(girAppIndicator.IndicatorStatus.ATTENTION)
        self.indicator.set_status(girAppIndicator.IndicatorStatus.ACTIVE)
