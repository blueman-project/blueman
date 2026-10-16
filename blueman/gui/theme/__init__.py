"""Branding and visual-theme helpers for the manager redesign.

GTK-dependent helpers intentionally live in their own modules so importing
brand constants does not initialize a display connection.
"""

from blueman.gui.theme.Brand import (
    ABOUT_BLURB,
    COPYRIGHT,
    DISPLAY_NAME,
    ICON_NAME,
    LICENSE_NAME,
    NOTIFICATION_APP_NAME,
    SHORT_DESCRIPTION,
    WEBSITE,
    about_text,
    window_title,
)

__all__ = [
    "ABOUT_BLURB",
    "COPYRIGHT",
    "DISPLAY_NAME",
    "ICON_NAME",
    "LICENSE_NAME",
    "NOTIFICATION_APP_NAME",
    "SHORT_DESCRIPTION",
    "WEBSITE",
    "about_text",
    "window_title",
]
