# coding=utf-8

from gi.repository import GObject, GLib

from blueman.Functions import launch, kill, get_pid, get_lockfile
from blueman.main.PluginManager import StopException
from blueman.plugins.AppletPlugin import AppletPlugin


class StatusIcon(AppletPlugin, GObject.GObject):
    __gsignals__ = {str('activate'): (GObject.SignalFlags.NO_HOOKS, None, ())}

    __unloadable__ = False
    __icon__ = "blueman-tray"
    __depends__ = ['Menu']

    FORCE_SHOW = 2
    SHOW = 1
    FORCE_HIDE = 0

    visible = None

    visibility_timeout = None

    _implementation = None

    def on_load(self):
        GObject.GObject.__init__(self)
        self.lines = {0: _("Bluetooth Enabled")}

        AppletPlugin.add_method(self.on_query_status_icon_implementation)
        AppletPlugin.add_method(self.on_query_status_icon_visibility)
        AppletPlugin.add_method(self.on_status_icon_query_icon)

        self.query_visibility(emit=False)

        self.parent.Plugins.connect('plugin-loaded', self._on_plugins_changed)
        self.parent.Plugins.connect('plugin-unloaded', self._on_plugins_changed)

        self._add_dbus_method("GetVisibility", (), "b", lambda: self.visible)
        self._add_dbus_signal("VisibilityChanged", "b")
        self._add_dbus_signal("TextChanged", "s")
        self._add_dbus_method("GetText", (), "s", self._get_text)
        self._add_dbus_signal("IconNameChanged", "s")
        self._add_dbus_method("GetStatusIconImplementation", (), "s", self._get_status_icon_implementation)
        self._add_dbus_method("GetIconName", (), "s", self._get_icon_name)
        self._add_dbus_method("Activate", (), "", lambda: self.emit("activate"))

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

    def set_visible(self, visible, emit):
        self.visible = visible
        if emit:
            self._emit_dbus_signal("VisibilityChanged", visible)

    def set_text_line(self, lineid, text):
        if text:
            self.lines[lineid] = text
        else:
            self.lines.pop(lineid, None)

        self._emit_dbus_signal("TextChanged", self._get_text())

    def _get_text(self):
        return '\n'.join([self.lines[key] for key in sorted(self.lines)])

    def icon_should_change(self):
        self._emit_dbus_signal("IconNameChanged", self._get_icon_name())
        self.query_visibility()

    def on_adapter_added(self, path):
        self.query_visibility()

    def on_adapter_removed(self, path):
        self.query_visibility()

    def on_manager_state_changed(self, state):
        self.query_visibility()

    def _on_plugins_changed(self, _plugins, _name):
        implementation = self._get_status_icon_implementation()
        if not self._implementation or self._implementation != implementation:
            self._implementation = implementation
            kill(get_pid(get_lockfile('blueman-tray')), 'blueman-tray')
            launch('blueman-tray', icon_name='blueman', sn=False)

    def _get_status_icon_implementation(self):
        implementations = self.parent.Plugins.run("on_query_status_icon_implementation")
        return next((implementation for implementation in implementations if implementation), 'GtkStatusIcon')

    def _get_icon_name(self):
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
