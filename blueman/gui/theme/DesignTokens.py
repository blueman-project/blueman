"""Design tokens for the Blueman Next visual system.

Design tokens are the named colour, spacing and animation values shared
between the GTK CSS files and the Python drawing code (e.g. the Bluetooth
radar, status indicators, custom widgets).  Keeping a single Python
module that mirrors the CSS custom-property values prevents the
presentation code from drifting away from the stylesheet.

GTK 3 does not support reading CSS custom properties from Python, so
this module is the authoritative source for any values that the
non-CSS code needs (radar rings, status indicator colours, etc.).
The CSS files in ``data/themes/`` carry the same values; if you change
one, change both.
"""

from __future__ import annotations

from typing import Final


# ---------------------------------------------------------------------------
# Dark theme palette
# ---------------------------------------------------------------------------

DARK_BG_PRIMARY: Final[str] = "#0B1118"
"""Primary background of the application window."""

DARK_BG_SECONDARY: Final[str] = "#121B25"
"""Secondary background used for layered surfaces (sidebar, inspector)."""

DARK_BG_CARD: Final[str] = "#1A2532"
"""Default card background used for device cards and list items."""

DARK_BG_ELEVATED: Final[str] = "#202D3C"
"""Hover and elevated card background."""

DARK_BG_INSPECTOR: Final[str] = "#0F1822"
"""Inspector panel surface, slightly darker than the secondary background."""

DARK_ACCENT_PRIMARY: Final[str] = "#477BFF"
"""Primary accent (focus rings, primary buttons, active state)."""

DARK_ACCENT_PRIMARY_HOVER: Final[str] = "#5C8FFF"
"""Hover state of the primary accent."""

DARK_ACCENT_PRIMARY_ACTIVE: Final[str] = "#2E5FE0"
"""Pressed/active state of the primary accent."""

DARK_ACCENT_SECONDARY: Final[str] = "#7C5CFF"
"""Secondary accent (gradients, pairing, success accents)."""

DARK_STATUS_CONNECTED: Final[str] = "#42D98B"
"""Connected status indicator."""

DARK_STATUS_WARNING: Final[str] = "#FFB84D"
"""Warning status indicator (battery low, blocking operation)."""

DARK_STATUS_DISCONNECTED: Final[str] = "#8B95A7"
"""Disconnected status indicator."""

DARK_STATUS_ERROR: Final[str] = "#FF6475"
"""Error status indicator."""

DARK_STATUS_CONNECTING: Final[str] = "#477BFF"
"""Connecting / pending status indicator."""

DARK_TEXT_PRIMARY: Final[str] = "#F5F7FB"
"""Primary text on dark surfaces."""

DARK_TEXT_SECONDARY: Final[str] = "#A2ADBE"
"""Secondary text on dark surfaces."""

DARK_TEXT_MUTED: Final[str] = "#697587"
"""Muted / placeholder text on dark surfaces."""

DARK_BORDER_SUBTLE: Final[str] = "rgba(255, 255, 255, 0.09)"
"""Default 1px border on cards and surfaces."""

DARK_BORDER_HOVER: Final[str] = "rgba(255, 255, 255, 0.16)"
"""Hover-state border colour."""

DARK_BORDER_FOCUS: Final[str] = "rgba(92, 143, 255, 0.75)"
"""Selection/focus border colour."""

# ---------------------------------------------------------------------------
# Light theme palette
# ---------------------------------------------------------------------------

LIGHT_BG_PRIMARY: Final[str] = "#F7F8FA"
"""Primary background of the application window in light theme."""

LIGHT_BG_SECONDARY: Final[str] = "#EEF1F5"
"""Secondary background used for layered surfaces (sidebar, inspector)."""

LIGHT_BG_CARD: Final[str] = "#FFFFFF"
"""Default card background used for device cards and list items."""

LIGHT_BG_ELEVATED: Final[str] = "#F2F4F8"
"""Hover and elevated card background."""

LIGHT_BG_INSPECTOR: Final[str] = "#FAFBFC"
"""Inspector panel surface, slightly tinted relative to primary."""

LIGHT_ACCENT_PRIMARY: Final[str] = "#2D5BFF"
"""Primary accent in light theme."""

LIGHT_ACCENT_PRIMARY_HOVER: Final[str] = "#1E47E6"
"""Hover state of the primary accent in light theme."""

LIGHT_ACCENT_PRIMARY_ACTIVE: Final[str] = "#1A3DCC"
"""Pressed/active state of the primary accent in light theme."""

LIGHT_ACCENT_SECONDARY: Final[str] = "#6A4BE0"
"""Secondary accent in light theme."""

LIGHT_STATUS_CONNECTED: Final[str] = "#1FAE6B"
"""Connected status indicator (light theme)."""

LIGHT_STATUS_WARNING: Final[str] = "#E08A1A"
"""Warning status indicator (light theme)."""

LIGHT_STATUS_DISCONNECTED: Final[str] = "#8A95A6"
"""Disconnected status indicator (light theme)."""

LIGHT_STATUS_ERROR: Final[str] = "#E04054"
"""Error status indicator (light theme)."""

LIGHT_STATUS_CONNECTING: Final[str] = "#2D5BFF"
"""Connecting / pending status indicator (light theme)."""

LIGHT_TEXT_PRIMARY: Final[str] = "#101622"
"""Primary text on light surfaces."""

LIGHT_TEXT_SECONDARY: Final[str] = "#4A5466"
"""Secondary text on light surfaces."""

LIGHT_TEXT_MUTED: Final[str] = "#7A8497"
"""Muted / placeholder text on light surfaces."""

LIGHT_BORDER_SUBTLE: Final[str] = "rgba(16, 22, 34, 0.08)"
"""Default 1px border on cards and surfaces (light theme)."""

LIGHT_BORDER_HOVER: Final[str] = "rgba(16, 22, 34, 0.16)"
"""Hover-state border colour (light theme)."""

LIGHT_BORDER_FOCUS: Final[str] = "rgba(45, 91, 255, 0.55)"
"""Selection/focus border colour (light theme)."""

# ---------------------------------------------------------------------------
# Device category accents
# ---------------------------------------------------------------------------

DEVICE_ACCENT_SPEAKER: Final[str] = "#FF8A4C"
DEVICE_ACCENT_HEADPHONES: Final[str] = "#7C5CFF"
DEVICE_ACCENT_PHONE: Final[str] = "#42A5F5"
DEVICE_ACCENT_KEYBOARD: Final[str] = "#26A69A"
DEVICE_ACCENT_MOUSE: Final[str] = "#AB7BFF"
DEVICE_ACCENT_CONTROLLER: Final[str] = "#EC407A"
DEVICE_ACCENT_COMPUTER: Final[str] = "#5C8FFF"
DEVICE_ACCENT_UNKNOWN: Final[str] = "#8B95A7"

# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------

RADIUS_CARD: Final[int] = 18
"""Default corner radius for device cards."""

RADIUS_PANEL: Final[int] = 14
"""Corner radius for sidebar, inspector and other panel surfaces."""

RADIUS_BUTTON: Final[int] = 10
"""Corner radius for action buttons."""

RADIUS_AVATAR: Final[int] = 16
"""Corner radius for device avatars."""

CARD_HEIGHT: Final[int] = 132
"""Default height of a device card."""

AVATAR_SIZE: Final[int] = 72
"""Default avatar size in device cards."""

SIDEBAR_WIDTH: Final[int] = 260
"""Default sidebar width in pixels."""

INSPECTOR_WIDTH: Final[int] = 340
"""Default inspector panel width in pixels."""

DEFAULT_WINDOW_WIDTH: Final[int] = 1400
DEFAULT_WINDOW_HEIGHT: Final[int] = 850
MIN_WINDOW_WIDTH: Final[int] = 900
MIN_WINDOW_HEIGHT: Final[int] = 600

# ---------------------------------------------------------------------------
# Animation
# ---------------------------------------------------------------------------

ANIMATION_DURATION_MS: Final[int] = 180
"""Default UI transition duration in milliseconds."""

ANIMATION_RADAR_FPS: Final[int] = 30
"""Target frame rate for decorative radar/scanning animations."""

ANIMATION_RADAR_FRAME_MS: Final[int] = 1000 // ANIMATION_RADAR_FPS
"""Single-frame interval for the radar animation in milliseconds."""


def status_color(name: str, dark: bool = True) -> str:
    """Return the colour string for a semantic status.

    :param name: one of ``"connected"``, ``"warning"``, ``"disconnected"``,
      ``"error"``, ``"connecting"`` or ``"pairing"``.
    :param dark: select the dark palette if ``True``, light otherwise.
    :returns: a CSS colour string suitable for Cairo ``set_source_rgb``
      or ``set_source_rgba`` (the alpha component, if any, is preserved
      from the original definition).
    """
    if dark:
        mapping = {
            "connected": DARK_STATUS_CONNECTED,
            "warning": DARK_STATUS_WARNING,
            "disconnected": DARK_STATUS_DISCONNECTED,
            "error": DARK_STATUS_ERROR,
            "connecting": DARK_STATUS_CONNECTING,
            "pairing": DARK_ACCENT_SECONDARY,
        }
    else:
        mapping = {
            "connected": LIGHT_STATUS_CONNECTED,
            "warning": LIGHT_STATUS_WARNING,
            "disconnected": LIGHT_STATUS_DISCONNECTED,
            "error": LIGHT_STATUS_ERROR,
            "connecting": LIGHT_STATUS_CONNECTING,
            "pairing": LIGHT_ACCENT_SECONDARY,
        }
    try:
        return mapping[name]
    except KeyError as exc:
        raise ValueError(f"Unknown status name: {name!r}") from exc


def device_accent(category: str) -> str:
    """Return the accent colour for a device category.

    The category string is matched case-insensitively against a small
    set of keywords.  Anything that does not match a known category
    returns the unknown-device accent.  Callers that have a richer
    classification (e.g. from ``blueman.DeviceClass``) should map to
    one of the supported keys before calling this function.
    """
    if not category:
        return DEVICE_ACCENT_UNKNOWN
    normalized = category.strip().lower()
    for keyword, color in (
        ("speaker", DEVICE_ACCENT_SPEAKER),
        ("audio", DEVICE_ACCENT_SPEAKER),
        ("headphone", DEVICE_ACCENT_HEADPHONES),
        ("headset", DEVICE_ACCENT_HEADPHONES),
        ("phone", DEVICE_ACCENT_PHONE),
        ("smartphone", DEVICE_ACCENT_PHONE),
        ("keyboard", DEVICE_ACCENT_KEYBOARD),
        ("mouse", DEVICE_ACCENT_MOUSE),
        ("controller", DEVICE_ACCENT_CONTROLLER),
        ("gamepad", DEVICE_ACCENT_CONTROLLER),
        ("computer", DEVICE_ACCENT_COMPUTER),
        ("laptop", DEVICE_ACCENT_COMPUTER),
    ):
        if keyword in normalized:
            return color
    return DEVICE_ACCENT_UNKNOWN
