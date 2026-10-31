"""Schema-backed settings page shown inside the redesigned manager window."""

from gettext import gettext as _

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Pango  # noqa: E402


# Only keys the redesigned window honours. show-toolbar/show-statusbar are left out:
# the classic toolbar and status bar are no longer displayed, so those switches did nothing.
EXPOSED_SETTINGS = frozenset({
    "hide-unnamed",
    "sort-by",
    "sort-descending",
    "notification-daemon",
    "symbolic-status-icons",
    "theme-variant",
    "reduced-motion",
})


class SegmentedChoice(Gtk.Box):
    """Pill-shaped radio group kept in sync with a string GSettings key."""

    def __init__(self, settings: Gio.Settings, key: str, choices: tuple[tuple[str, str], ...]) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, valign=Gtk.Align.CENTER, visible=True)
        self.get_style_context().add_class("segmented")
        self.get_style_context().add_class("linked")
        self._settings = settings
        self._key = key
        self.buttons: dict[str, Gtk.RadioButton] = {}
        group: Gtk.RadioButton | None = None
        for value, label in choices:
            button = Gtk.RadioButton(label=label, visible=True)
            button.join_group(group)
            button.set_mode(False)
            button.connect("toggled", self._on_toggled, value)
            self.pack_start(button, False, False, 0)
            self.buttons[value] = button
            group = group or button
        self._sync()
        self._handler = settings.connect(f"changed::{key}", lambda _settings, _key: self._sync())
        self.connect("destroy", lambda _widget: settings.disconnect(self._handler))

    def _sync(self) -> None:
        button = self.buttons.get(self._settings.get_string(self._key))
        if button is not None and not button.get_active():
            button.set_active(True)

    def _on_toggled(self, button: Gtk.RadioButton, value: str) -> None:
        if button.get_active() and self._settings.get_string(self._key) != value:
            self._settings.set_string(self._key, value)


class ManagerSettingsPage(Gtk.ScrolledWindow):
    def __init__(self, application: Gtk.Application, settings: Gio.Settings) -> None:
        super().__init__(
            hscrollbar_policy=Gtk.PolicyType.NEVER,
            hexpand=True,
            vexpand=True,
            visible=True,
        )
        self.get_style_context().add_class("settings-scroll")
        self._application = application
        self._settings = settings
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20, visible=True)
        content.get_style_context().add_class("settings-page")
        self.add(content)

        title = Gtk.Label(label=_("Settings"), xalign=0, visible=True)
        title.get_style_context().add_class("dashboard-title")
        subtitle = Gtk.Label(
            label=_("Choose how Bluetooth looks and behaves on this computer."),
            xalign=0,
            wrap=True,
            visible=True,
        )
        subtitle.get_style_context().add_class("dashboard-subtitle")
        heading = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4, visible=True)
        heading.get_style_context().add_class("settings-heading")
        heading.pack_start(title, False, False, 0)
        heading.pack_start(subtitle, False, False, 0)
        content.pack_start(heading, False, False, 0)

        self.controls: dict[str, Gtk.Widget] = {}

        general = self._section(content, _("Devices"))
        self._row(general, "view-list-symbolic", _("Sort devices by"),
                  _("Order of devices inside each section."),
                  self._choice("sort-by", (("timestamp", _("Recently seen")), ("alias", _("Name")))))
        self._row(general, "view-sort-descending-symbolic", _("Reverse sort order"),
                  _("Show the oldest or last-named devices first."), self._switch("sort-descending"))
        self._row(general, "view-conceal-symbolic", _("Hide unnamed devices"),
                  _("Skip devices that only advertise an address."), self._switch("hide-unnamed"), last=True)

        appearance = self._section(content, _("Appearance"))
        self._row(appearance, "weather-clear-night-symbolic", _("Color scheme"),
                  _("Follow the desktop or keep a fixed look."),
                  self._choice("theme-variant", (("system", _("System")), ("dark", _("Dark")), ("light", _("Light")))))
        self._row(appearance, "preferences-desktop-accessibility-symbolic", _("Reduce motion"),
                  _("Turn off page transitions and the scanning pulse."), self._switch("reduced-motion"), last=True)

        notifications = self._section(content, _("Notifications"))
        self._row(notifications, "preferences-system-notifications-symbolic", _("Desktop notifications"),
                  _("Use the desktop's notification service."), self._switch("notification-daemon"))
        self._row(notifications, "emblem-photos-symbolic", _("Symbolic tray icons"),
                  _("Monochrome icons that match the panel."), self._switch("symbolic-status-icons"), last=True)

        system = self._section(content, _("Bluetooth System"))
        for icon_name, label, description, action in (
            ("bluetooth-active-symbolic", _("Adapter Settings"), _("Name, visibility and discovery timeout."),
             "preferences"),
            ("network-workgroup-symbolic", _("Service Preferences"), _("Network access and file transfer."),
             "services"),
            ("application-x-addon-symbolic", _("Plugin Manager"), _("Enable or configure applet plugins."),
             "plugins"),
        ):
            self._link_row(system, icon_name, label, description, action)

    @staticmethod
    def _section(parent: Gtk.Box, title: str) -> Gtk.Box:
        section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, visible=True)
        for css_class in ("inspector-section", "settings-section"):
            section.get_style_context().add_class(css_class)
        label = Gtk.Label(label=title, xalign=0, visible=True)
        label.get_style_context().add_class("inspector-section-title")
        section.pack_start(label, False, False, 0)
        parent.pack_start(section, False, False, 0)
        return section

    @staticmethod
    def _row_content(icon_name: str, title: str, description: str) -> Gtk.Box:
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16, visible=True)
        badge = Gtk.Box(valign=Gtk.Align.CENTER, visible=True)
        badge.get_style_context().add_class("quick-action-badge")
        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
        icon.show()
        badge.pack_start(icon, True, True, 0)
        texts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2, valign=Gtk.Align.CENTER, visible=True)
        heading = Gtk.Label(label=title, xalign=0, visible=True)
        heading.get_style_context().add_class("settings-row-title")
        detail = Gtk.Label(label=description, xalign=0, ellipsize=Pango.EllipsizeMode.END, visible=True)
        detail.get_style_context().add_class("settings-row-subtitle")
        texts.pack_start(heading, False, False, 0)
        texts.pack_start(detail, False, False, 0)
        row.pack_start(badge, False, False, 0)
        row.pack_start(texts, True, True, 0)
        return row

    def _row(self, section: Gtk.Box, icon_name: str, title: str, description: str,
             control: Gtk.Widget, last: bool = False) -> None:
        row = self._row_content(icon_name, title, description)
        row.get_style_context().add_class("settings-row")
        if last:
            row.get_style_context().add_class("settings-row-last")
        row.pack_end(control, False, False, 0)
        section.pack_start(row, False, False, 0)

    def _link_row(self, section: Gtk.Box, icon_name: str, title: str, description: str, action: str) -> None:
        button = Gtk.Button(visible=True)
        button.get_style_context().add_class("settings-link")
        content = self._row_content(icon_name, title, description)
        arrow = Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        arrow.show()
        arrow.get_style_context().add_class("quick-action-arrow")
        content.pack_end(arrow, False, False, 0)
        button.add(content)
        button.connect("clicked", self._activate, action)
        self.controls[action] = button
        section.pack_start(button, False, False, 0)

    def _activate(self, _button: Gtk.Button, action: str) -> None:
        self._application.activate_action(action, None)

    def _switch(self, key: str) -> Gtk.Switch:
        switch = Gtk.Switch(valign=Gtk.Align.CENTER, visible=True)
        self._settings.bind(key, switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self.controls[key] = switch
        return switch

    def _choice(self, key: str, choices: tuple[tuple[str, str], ...]) -> SegmentedChoice:
        choice = SegmentedChoice(self._settings, key, choices)
        self.controls[key] = choice
        return choice
