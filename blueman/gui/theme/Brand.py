"""Centralized brand identity for Blueman Next.

This module exposes a single source of truth for the user-facing identity of
the application (display name, short description, About text, notification
app name, icon name and homepage).  It deliberately does NOT expose the
D-Bus names, GSettings schema IDs, Python package name, executable names
or systemd units; those internal identifiers are preserved exactly as in
upstream Blueman (see ``blueman.Constants``) and must not be renamed
without an explicit migration plan.

The values are written here once and read via plain module attributes
so that downstream code never has to duplicate the brand string in
multiple places.  When the final display name is chosen, change the
``DISPLAY_NAME`` and ``SHORT_DESCRIPTION`` constants below; everything
that imports from this module will pick up the new value.
"""

from __future__ import annotations

from typing import Optional

from gettext import gettext as _

from blueman.Constants import (
    BRAND_DESCRIPTION,
    BRAND_DISPLAY_NAME,
    BRAND_ICON_NAME,
    BRAND_NOTIFICATION_APP_NAME,
    WEBSITE,
)

DISPLAY_NAME: str = BRAND_DISPLAY_NAME
"""User-facing name of the application shown in window titles, About
dialogs, notifications and other user-visible surfaces."""

SHORT_DESCRIPTION: str = BRAND_DESCRIPTION
"""Short tagline used in the About dialog and the desktop file
``Comment`` field."""

APP_ID: str = "org.blueman.Manager"
"""The stable application ID used for ``Gio.Application`` registration.
This intentionally matches the existing D-Bus application ID so that
existing single-instance semantics and saved GSettings state continue
to work without any migration step."""

NOTIFICATION_APP_NAME: str = BRAND_NOTIFICATION_APP_NAME
"""Application name sent to the freedesktop notification daemon.  Kept
identical to the display name by default; override here only if a
shorter identity is required for compact notification banners."""

NOTIFICATION_REPLACE_ID: str = "blueman"
"""``replaces_id`` we hand to the notification daemon.  We keep the
legacy identifier so that desktop notification stacks (which key on
replaces_id) can deduplicate old and new branding entries without a
reset of user state."""

ICON_NAME: str = BRAND_ICON_NAME
"""The freedesktop icon name used by the application windows.  Stays
on the legacy ``blueman`` icon until new brand artwork is shipped."""

COPYRIGHT: str = "(C) 2008 - 2026 blueman developers"
"""Copyright string shown in the About dialog.  Preserved from upstream
to satisfy attribution requirements; do not remove the original
holders."""

LICENSE_NAME: str = "GPL-3.0+"
"""Short license name shown in the About dialog."""

ABOUT_BLURB: str = _(
    "{display} is a GTK+ Bluetooth manager designed to provide a modern, "
    "streamlined interface for managing Bluetooth adapters, pairing with "
    "nearby devices, sending files over OBEX and configuring audio and "
    "network profiles."
).format(display=DISPLAY_NAME)
"""Long-form description shown in the About dialog.  The string is
pre-translated at import time; translators can update the
gettext catalogs without modifying Python code."""


def about_text(version: str) -> str:
    """Return a fully formatted About dialog body.

    :param version: the application version string, e.g. ``"2.4.3"``.
    :returns: a multi-line string suitable for ``Gtk.AboutDialog`` or
      a custom About presentation.
    """
    return (
        f"{DISPLAY_NAME}\n"
        f"{SHORT_DESCRIPTION}\n\n"
        f"{ABOUT_BLURB}\n\n"
        f"{_('Version')}: {version}\n"
        f"{COPYRIGHT}\n"
        f"{_('License')}: {LICENSE_NAME}\n"
        f"{_('Website')}: {WEBSITE}"
    )


def window_title(section: Optional[str] = None) -> str:
    """Return the title text for a top-level window.

    :param section: optional sub-section, e.g. ``"Settings"``.
    :returns: ``"Blueman Next"`` or ``"Blueman Next — Settings"``.
    """
    if section:
        return f"{DISPLAY_NAME} \u2014 {section}"
    return DISPLAY_NAME
