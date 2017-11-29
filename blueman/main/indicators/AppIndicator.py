# coding=utf-8
import gi

gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3
from blueman.main.indicators.GtkStatusIcon import build_menu


class AppIndicator(object):
    def __init__(self, icon_name, on_activate_menu_item, _on_activate_status_icon):
        self._on_activate = on_activate_menu_item
        self.indicator = AppIndicator3.Indicator.new('blueman', icon_name,
                                                     AppIndicator3.IndicatorCategory.APPLICATION_STATUS)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    def set_icon(self, icon_name):
        self.indicator.set_icon(icon_name)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ATTENTION)
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

    def set_text(self, text):
        self.indicator.props.title = text

    def set_visibility(self, visible):
        status = AppIndicator3.IndicatorStatus.ACTIVE if visible else AppIndicator3.IndicatorStatus.PASSIVE
        self.indicator.set_status(status)

    def set_menu(self, menu):
        self.indicator.set_menu(build_menu(menu, self._on_activate))
