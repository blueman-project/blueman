# Copyright (C) 2011 Valmantas Paliksa <walmis at balticum-tv dot lt>
# Copyright (C) 2011 Tadas Dailyda <tadas at dailyda dot com>
#
# Licensed under the GNU General Public License Version 3
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 

#from blueman.Functions import *

from blueman.Constants import *
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.main.applet.BluezAgent import AdapterAgent
import blueman.bluez as Bluez

from gi.repository import GObject
import os
from gi.repository import AppIndicator3 as girAppIndicator

class AppIndicator(AppletPlugin):
    __description__ = _("Uses libappindicator to show a statusicon")
    __icon__ = "blueman"
    __author__ = "Walmis"
    __depends__ = ["StatusIcon", "Menu"]
    
    def on_load(self, applet):
        
        self.indicator = girAppIndicator.Indicator.new ("blueman",
                                                        applet.Plugins.StatusIcon.get_option("icon"),
                                                        girAppIndicator.IndicatorCategory.APPLICATION_STATUS)
        
        self.indicator.set_status (girAppIndicator.IndicatorStatus.ACTIVE)
        
        self.indicator.set_menu(applet.Plugins.Menu.get_menu())
        
        self.s =  self.Applet.Plugins.StatusIcon.connect("notify::icon-name", self.on_notify)

        #self.Applet.Plugins.StatusIcon.set_visible = partial(self.set_visible, self.Applet.Plugins.StatusIcon)
        self.override_method(self.Applet.Plugins.StatusIcon, "set_visible", self.set_visible)
        
        self.Applet.Plugins.StatusIcon.props.visible = False

    def set_visible(self, statusicon, visible):
        if visible:
            self.indicator.set_status(girAppIndicator.IndicatorStatus.ACTIVE)
        else:
            self.indicator.set_status(girAppIndicator.IndicatorStatus.PASSIVE)
        
    def on_notify(self, *args):
        self.update_icon()
        
    def on_unload(self):
        #self.indicator.set_menu(None)
        del self.indicator
        self.Applet.Plugins.StatusIcon.QueryVisibility()
        self.Applet.Plugins.StatusIcon.disconnect(self.s)
        
    #def on_status_icon_pixbuf_ready(self):
    #    print "aaaaa"
    #    GObject.idle_add(self.update_icon)
        
    def update_icon(self):
        
        self.indicator.set_icon(self.Applet.Plugins.StatusIcon.props.icon_name)
        self.indicator.set_status(girAppIndicator.IndicatorStatus.ATTENTION)
        self.indicator.set_status(girAppIndicator.IndicatorStatus.ACTIVE)
        
