# Changelog

## master

### Changes

* [obex] Switch to obexd for sending files
* [browse] Use system's default browser for obex URI if no browse command is set

### Bugs fixed

* [ui] Make some UI elements expand again (@infirit / Sander Sweers)
* Fix crash in PluginManager (Martín Ferrari)
* Avoid crash in transfer service setup dialog
* Make blueman-applet respond to SIGTERM (@Teknocrat / Harvey Mittens)
* Allow setting friendly adapter name in BlueZ 5
* Look for both dhcpd and dhcpd3 and add sbin paths (@infirit / Sander Sweers)
* Respect custom status icon

## 1.99.alpha1

### New features

* dhcpcd client support (@Teknocrat / Harvey Mittens)
* Partial support for BlueZ 5 (see #13 for the current state)

### Changes

* Switch to GTK+ 3 (using introspection)
* Update autoconf to support aarch64 (Dennis Gilmore)
* Migrate from Pyrex to Cython (@Teknocrat / Harvey Mittens)

### Bugs fixed

* Fix nautilus integration
* Fix pulseaudio version check
* Add missing icons
* Fix initial applet state if bluetooth is disabled
* Fix blueman startup when .cache dir doesn't exist (@asdil12 / Dominik Heidler)
* Fix thunar fallback (Jan Hutař)
* Do not power new adapters despite rfkill (@lkr / Leesa)
* Fix handling of network devices (especially fixes DhcpClient plugin)
* Update translations (too many to list them)
* Fix nonexistent dbus exception (Martín Ferrari)
* Fix a rare problem when the manager device menu cannot get the current selection (@kolen / Konstantin Mochalov)
* Fix pulseaudio device discovery (see #64 and the linked Ubuntu bugs for details and contributors)
