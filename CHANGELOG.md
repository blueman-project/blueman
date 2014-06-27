# Changelog

## master

* Fix nautilus integration
* Fix pulseaudio version check
* Add missing icons
* Fix initial applet state if bluetooth is disabled
* Fix blueman startup when .cache dir doesn't exist (@asdil12 / Dominik Heidler)
* Fix thunar fallback (Jan Hutař)
* Update autoconf to support aarch64 (Dennis Gilmore)
* Do not power new adapters despite rfkill (@lkr / Leesa)
* Switch to GTK+ 3 (using introspection)
* Fix handling of network devices (especially fixes DhcpClient plugin)
* Update translations (too many to list them)
* Prefer the GTK theme's bluetooth icons over the shipped ones (@Teknocrat)
* Fix nonexistent dbus exception (Martín Ferrari)
* Fix a rare problem when the manager device menu cannot get the current selection (@kolen / Konstantin Mochalov)
* dhcpcd client support (@Teknocrat)
* Fix pulseaudio device discovery (see #64 and the linked Ubuntu bugs for details and contributors)
