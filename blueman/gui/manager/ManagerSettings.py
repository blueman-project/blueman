"""Schema-backed settings dialog for the redesigned manager."""

from gettext import gettext as _

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk  # noqa: E402


EXPOSED_SETTINGS = frozenset({
    "hide-unnamed",
    "sort-by",
    "sort-descending",
    "notification-daemon",
    "symbolic-status-icons",
    "theme-variant",
    "reduced-motion",
    "show-toolbar",
    "show-statusbar",
})


class ManagerSettingsDialog(Gtk.Dialog):
    def __init__(self, parent: Gtk.Window, application: Gtk.Application, settings: Gio.Settings) -> None:
        super().__init__(
            title=_("Settings"),
            transient_for=parent,
            modal=True,
            destroy_with_parent=True,
            use_header_bar=True,
        )
        self.set_default_size(720, 520)
        self.add_button(_("Close"), Gtk.ResponseType.CLOSE)
        self.connect("response", lambda dialog, _response: dialog.destroy())

        stack = Gtk.Stack(
            transition_type=Gtk.StackTransitionType.CROSSFADE,
            transition_duration=0 if settings.get_boolean("reduced-motion") else 180,
            hexpand=True,
            vexpand=True,
            visible=True,
        )
        sidebar = Gtk.StackSidebar(stack=stack, width_request=190, visible=True)
        layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0, visible=True)
        layout.pack_start(sidebar, False, False, 0)
        layout.pack_start(stack, True, True, 0)
        self.get_content_area().pack_start(layout, True, True, 0)

        general = self._page()
        self._switch_row(general, settings, "hide-unnamed", _("Hide unnamed devices"))
        self._choice_row(general, settings, "sort-by", _("Sort devices by"), (
            ("timestamp", _("Recently seen")), ("alias", _("Name")),
        ))
        self._switch_row(general, settings, "sort-descending", _("Reverse sort order"))
        stack.add_titled(general, "general", _("General"))

        appearance = self._page()
        self._choice_row(appearance, settings, "theme-variant", _("Color scheme"), (
            ("system", _("System")), ("dark", _("Dark")), ("light", _("Light")),
        ))
        self._switch_row(appearance, settings, "reduced-motion", _("Reduce interface motion"))
        stack.add_titled(appearance, "appearance", _("Appearance"))

        notifications = self._page()
        self._switch_row(notifications, settings, "notification-daemon", _("Use desktop notifications"))
        self._switch_row(notifications, settings, "symbolic-status-icons", _("Use symbolic tray icons"))
        stack.add_titled(notifications, "notifications", _("Notifications"))

        advanced = self._page()
        self._switch_row(advanced, settings, "show-toolbar", _("Show classic toolbar"))
        self._switch_row(advanced, settings, "show-statusbar", _("Show classic status bar"))
        for label, action in (
            (_("Adapter Settings"), "preferences"),
            (_("Service Preferences"), "services"),
            (_("Plugin Manager"), "plugins"),
        ):
            button = Gtk.Button(label=label, visible=True)
            button.get_style_context().add_class("secondary-button")
            button.connect("clicked", lambda _button, name=action: application.activate_action(name, None))
            advanced.pack_start(button, False, False, 0)
        stack.add_titled(advanced, "advanced", _("Advanced"))
        motion_handler = settings.connect(
            "changed::reduced-motion",
            lambda current, _key: stack.set_transition_duration(
                0 if current.get_boolean("reduced-motion") else 180
            ),
        )
        self.connect("destroy", lambda _dialog: settings.disconnect(motion_handler))
        self.show_all()

    @staticmethod
    def _page() -> Gtk.Box:
        return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=24, visible=True)

    @staticmethod
    def _switch_row(page: Gtk.Box, settings: Gio.Settings, key: str, label: str) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, visible=True)
        row.get_style_context().add_class("inspector-row")
        title = Gtk.Label(label=label, xalign=0, visible=True)
        switch = Gtk.Switch(valign=Gtk.Align.CENTER, visible=True)
        settings.bind(key, switch, "active", Gio.SettingsBindFlags.DEFAULT)
        row.pack_start(title, True, True, 0)
        row.pack_end(switch, False, False, 0)
        page.pack_start(row, False, False, 0)

    @staticmethod
    def _choice_row(
        page: Gtk.Box,
        settings: Gio.Settings,
        key: str,
        label: str,
        choices: tuple[tuple[str, str], ...],
    ) -> None:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12, visible=True)
        title = Gtk.Label(label=label, xalign=0, visible=True)
        combo = Gtk.ComboBoxText(visible=True)
        for value, text in choices:
            combo.append(value, text)
        settings.bind(key, combo, "active-id", Gio.SettingsBindFlags.DEFAULT)
        row.pack_start(title, True, True, 0)
        row.pack_end(combo, False, False, 0)
        page.pack_start(row, False, False, 0)
