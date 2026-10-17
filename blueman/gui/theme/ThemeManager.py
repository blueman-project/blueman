"""Lifecycle management for the optional Blueman GTK 3 color themes."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

from blueman.Constants import THEME_PATH

log = logging.getLogger(__name__)


class ThemeMode:
    SYSTEM = "system"
    DARK = "dark"
    LIGHT = "light"
    ALL = (SYSTEM, DARK, LIGHT)


class ThemeManager:
    """Own the application palette selected explicitly or from the desktop.

    ``system`` follows the desktop's light/dark preference but still loads the
    Blueman Next design system.  Previously it installed no provider at all,
    which made the default setting render as the legacy desktop theme.
    """

    _instance: Optional["ThemeManager"] = None

    def __init__(self, screen: Optional[Gdk.Screen] = None) -> None:
        self._screen = screen if screen is not None else Gdk.Screen.get_default()
        self._providers: dict[str, Gtk.CssProvider] = {}
        self._settings: Optional[Gio.Settings] = None
        self._settings_signal_id = 0
        self._gtk_settings_signal_id = 0
        self._requested_mode = ThemeMode.SYSTEM
        self._resolved_mode = ThemeMode.LIGHT
        self._current_provider: Optional[Gtk.CssProvider] = None

    @classmethod
    def get_default(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @staticmethod
    def themes_dir() -> Path:
        return THEME_PATH

    def load(self) -> None:
        """Parse bundled stylesheets without changing the active theme."""
        providers: dict[str, Gtk.CssProvider] = {}
        for mode in (ThemeMode.DARK, ThemeMode.LIGHT):
            path = self.themes_dir() / f"{mode}.css"
            provider = Gtk.CssProvider()
            try:
                provider.load_from_path(str(path))
            except GLib.Error as error:
                log.warning("Failed to load theme %s: %s", path, error.message)
                continue
            providers[mode] = provider
        self._providers = providers

    def apply(self, settings: Optional[Gio.Settings] = None) -> None:
        """Apply and monitor the appearance preference."""
        if not self._providers:
            self.load()

        new_settings = settings or Gio.Settings(schema_id="org.blueman.general")
        if new_settings is not self._settings:
            if self._settings is not None and self._settings_signal_id:
                self._settings.disconnect(self._settings_signal_id)
            self._settings = new_settings
            self._settings_signal_id = self._settings.connect(
                "changed", self._on_settings_changed
            )

        gtk_settings = Gtk.Settings.get_default()
        if gtk_settings is not None and not self._gtk_settings_signal_id:
            self._gtk_settings_signal_id = gtk_settings.connect(
                "notify::gtk-theme-name", self._on_desktop_theme_changed
            )
        self.refresh()

    def refresh(self) -> None:
        requested = ThemeMode.SYSTEM
        if self._settings is not None:
            requested = self._settings.get_string("theme-variant")
        if requested not in ThemeMode.ALL:
            log.warning("Ignoring unknown theme variant %r", requested)
            requested = ThemeMode.SYSTEM

        self._remove_current_provider()
        self._requested_mode = requested
        self._resolved_mode = self._detect_system_mode() if requested == ThemeMode.SYSTEM else requested

        if self._screen is None:
            return
        provider = self._providers.get(self._resolved_mode)
        if provider is not None:
            Gtk.StyleContext.add_provider_for_screen(
                self._screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            self._current_provider = provider

    def mode(self) -> str:
        return self._resolved_mode

    def requested_mode(self) -> str:
        return self._requested_mode

    def prefers_dark(self) -> bool:
        return self._resolved_mode == ThemeMode.DARK

    def reduced_motion(self) -> bool:
        return bool(self._settings and self._settings.get_boolean("reduced-motion"))

    def close(self) -> None:
        """Disconnect settings handlers and remove the active provider."""
        self._remove_current_provider()
        if self._settings is not None and self._settings_signal_id:
            self._settings.disconnect(self._settings_signal_id)
        self._settings = None
        self._settings_signal_id = 0
        gtk_settings = Gtk.Settings.get_default()
        if gtk_settings is not None and self._gtk_settings_signal_id:
            gtk_settings.disconnect(self._gtk_settings_signal_id)
        self._gtk_settings_signal_id = 0

    def _remove_current_provider(self) -> None:
        if self._current_provider is not None and self._screen is not None:
            Gtk.StyleContext.remove_provider_for_screen(
                self._screen, self._current_provider
            )
        self._current_provider = None

    @staticmethod
    def _detect_system_mode() -> str:
        settings = Gtk.Settings.get_default()
        if settings is None:
            return ThemeMode.LIGHT
        theme_name = (settings.props.gtk_theme_name or "").lower()
        prefer_dark = bool(settings.props.gtk_application_prefer_dark_theme)
        return ThemeMode.DARK if prefer_dark or "dark" in theme_name else ThemeMode.LIGHT

    def _on_settings_changed(self, _settings: Gio.Settings, key: str) -> None:
        if key == "theme-variant":
            self.refresh()

    def _on_desktop_theme_changed(self, _settings: Gtk.Settings, _pspec: object) -> None:
        if self._requested_mode == ThemeMode.SYSTEM:
            self.refresh()
