# Branding

User-facing identity is defined in `data/branding.json`. Both Meson and
Autotools read that file when generating Python constants and desktop entry
templates. Change the values there rather than duplicating the application
name in build metadata or Python code.

The redesign does **not** rename compatibility-sensitive identifiers. The
`blueman` Python package and executables, `org.blueman.*` D-Bus and GSettings
IDs, plugin names, systemd units, and the existing icon name remain stable.
