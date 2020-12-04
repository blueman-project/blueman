from gettext import gettext as _
from typing import Optional

from gi.repository import GObject, GLib

from blueman.Functions import launch
from blueman.main.PluginManager import PluginManager
from blueman.plugins.AppletPlugin import AppletPlugin
from blueman.bluemantyping import GSignals


class StatusIconImplementationProvider:
    def on_query_status_icon_implementation(self) -> Optional[str]:
        ...


class StatusIconVisibilityHandler:
    def on_query_force_status_icon_visibility(self) -> bool:
        ...


class StatusIconProvider:
    def on_status_icon_query_icon(self) -> Optional[str]:
        ...


class StatusIcon(AppletPlugin, GObject.GObject):
    __gsignals__: GSignals = {'activate': (GObject.SignalFlags.NO_HOOKS, None, ())}

    __unloadable__ = False
    __icon__ = "blueman-tray"
    __depends__ = ['Menu']

    visible = None

    visibility_timeout = None

    _implementation = None

    def on_load(self) -> None:
        GObject.GObject.__init__(self)
        self.lines = {0: _("Bluetooth Enabled")}

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

    def query_visibility(self, delay_hiding: bool = False, emit: bool = True) -> None:
        if self.parent.Manager.get_adapters() or \
           any(plugin.on_query_force_status_icon_visibility()
               for plugin in self.parent.Plugins.get_loaded_plugins(StatusIconVisibilityHandler)):
            self.set_visible(True, emit)
        elif not self.visibility_timeout:
            if delay_hiding:
                self.visibility_timeout = GLib.timeout_add(1000, self.on_visibility_timeout)
            else:
                self.set_visible(False, emit)

    def on_visibility_timeout(self) -> bool:
        assert self.visibility_timeout is not None
        GLib.source_remove(self.visibility_timeout)
        self.visibility_timeout = None
        self.query_visibility()
        return False

    def set_visible(self, visible: bool, emit: bool) -> None:
        self.visible = visible
        if emit:
            self._emit_dbus_signal("VisibilityChanged", visible)

    def set_text_line(self, lineid: int, text: str) -> None:
        if text:
            self.lines[lineid] = text
        else:
            self.lines.pop(lineid, None)

        self._emit_dbus_signal("TextChanged", self._get_text())

    def _get_text(self) -> str:
        return '\n'.join([self.lines[key] for key in sorted(self.lines)])

    def icon_should_change(self) -> None:
        self._emit_dbus_signal("IconNameChanged", self._get_icon_name())
        self.query_visibility()

    def on_adapter_added(self, _path: str) -> None:
        self.query_visibility()

    def on_adapter_removed(self, _path: str) -> None:
        self.query_visibility()

    def on_manager_state_changed(self, state: bool) -> None:
        self.query_visibility()
        if state:
            launch('blueman-tray', icon_name='blueman', sn=False)

    def _on_plugins_changed(self, _plugins: PluginManager, _name: str) -> None:
        implementation = self._get_status_icon_implementation()
        if not self._implementation or self._implementation != implementation:
            self._implementation = implementation

        if self.parent.manager_state:
            launch('blueman-tray', icon_name='blueman', sn=False)

    def _get_status_icon_implementation(self) -> str:
        for plugin in self.parent.Plugins.get_loaded_plugins(StatusIconImplementationProvider):
            implementation = plugin.on_query_status_icon_implementation()
            if implementation:
                return implementation
        return "GtkStatusIcon"

    def _get_icon_name(self) -> str:
        for plugin in self.parent.Plugins.get_loaded_plugins(StatusIconProvider):
            icon = plugin.on_status_icon_query_icon()
            if icon is not None:
                return icon
        return "blueman-tray"
