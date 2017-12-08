# coding=utf-8

import dbus.service
from gi.repository import GObject, GLib

from blueman.main.DBusProxies import TrayService
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin


class StatusIcon(AppletPlugin, GObject.GObject):
    __gsignals__ = {str('activate'): (GObject.SignalFlags.NO_HOOKS, None, ())}

    __author__ = "Walmis"
    __unloadable__ = False
    __icon__ = "blueman-tray"
    __description__ = _("Add icon with menu to system tray.")
    __depends__ = ['Menu']

    FORCE_SHOW = 2
    SHOW = 1
    FORCE_HIDE = 0

    visible = None

    visibility_timeout = None

    _implementation = None
    _tray = None

    def on_load(self):
        GObject.GObject.__init__(self)
        self.lines = {0: _("Bluetooth Enabled")}

        AppletPlugin.add_method(self.on_query_status_icon_implementation)
        AppletPlugin.add_method(self.on_query_status_icon_visibility)
        AppletPlugin.add_method(self.on_status_icon_query_icon)

        self.query_visibility(emit=False)

    def on_power_state_changed(self, _manager, state):
        if state:
            self.set_text_line(0, _("Bluetooth Enabled"))
            self.query_visibility(delay_hiding=True)
        else:
            self.set_text_line(0, _("Bluetooth Disabled"))
            self.query_visibility()

    def query_visibility(self, delay_hiding=False, emit=True):
        rets = self.parent.Plugins.run("on_query_status_icon_visibility")
        if StatusIcon.FORCE_HIDE not in rets:
            if StatusIcon.FORCE_SHOW in rets:
                self.set_visible(True, emit)
            else:
                if not self.parent.Manager:
                    self.set_visible(False, emit)
                    return

                if self.parent.Manager.get_adapters():
                    self.set_visible(True, emit)
                elif not self.visibility_timeout:
                    if delay_hiding:
                        self.visibility_timeout = GLib.timeout_add(1000, self.on_visibility_timeout)
                    else:
                        self.set_visible(False, emit)
        else:
            self.set_visible(False, emit)

    def on_visibility_timeout(self):
        GLib.source_remove(self.visibility_timeout)
        self.visibility_timeout = None
        self.query_visibility()

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="b")
    def GetVisibility(self):
        return self.visible

    def set_visible(self, visible, emit):
        self.visible = visible
        if emit:
            self.VisibilityChanged(visible)

    @dbus.service.signal('org.blueman.Applet', signature='b')
    def VisibilityChanged(self, visible):
        pass

    def set_text_line(self, lineid, text):
        if text:
            self.lines[lineid] = text
        else:
            self.lines.pop(lineid, None)

        self.TextChanged(self.GetText())

    @dbus.service.signal('org.blueman.Applet', signature='s')
    def TextChanged(self, text):
        pass

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="s")
    def GetText(self):
        return '\n'.join([self.lines[key] for key in sorted(self.lines)])

    def icon_should_change(self):
        self.IconNameChanged(self.GetIconName())
        self.query_visibility()

    @dbus.service.signal('org.blueman.Applet', signature='s')
    def IconNameChanged(self, icon_name):
        pass

    def on_adapter_added(self, path):
        self.query_visibility()

    def on_adapter_removed(self, path):
        self.query_visibility()

    def on_manager_state_changed(self, state):
        self.query_visibility()
        if state:
            self.parent.Plugins.connect('plugin-loaded', self._on_plugins_changed)
            self.parent.Plugins.connect('plugin-unloaded', self._on_plugins_changed)
            self._on_plugins_changed(None, None)
        else:
            self.parent.Plugins.disconnect_by_func(self._on_plugins_changed)

    def _on_plugins_changed(self, _plugins, _name):
        implementation = self.GetStatusIconImplementation()
        if not self._implementation:
            self._implementation = implementation
            self._tray = TrayService()
        elif self._implementation != implementation:
            self._implementation = implementation
            self._tray.restart()

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="s")
    def GetStatusIconImplementation(self):
        implementations = self.parent.Plugins.run("on_query_status_icon_implementation")
        return next((implementation for implementation in implementations if implementation), 'GtkStatusIcon')

    @dbus.service.method('org.blueman.Applet', in_signature="", out_signature="s")
    def GetIconName(self):
        icon = "blueman-tray"

        def callback(inst, ret):
            if ret is not None:
                for i in ret:
                    nonlocal icon
                    icon = i
                    raise StopException

        self.parent.Plugins.run_ex("on_status_icon_query_icon", callback)
        return icon

    def on_query_status_icon_implementation(self):
        return None

    def on_query_status_icon_visibility(self):
        return StatusIcon.SHOW

    def on_status_icon_query_icon(self):
        return None

    @dbus.service.method('org.blueman.Applet', in_signature="")
    def Activate(self):
        self.emit('activate')
