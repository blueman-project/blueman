# Changelog

## master

### New features

* Support for Python 3.3.
* [dhcp] udhcpc (busybox) support
* [dhcp] udhcpd (busybox) support

### Changes

* [ui] Button to reset device alias
* [bluez] Agent capability KeyboardDisplay (@kemnade-uni / Andreas Kemnade)
* New configuration option to disable the use of a notification daemon
* [sendto] Removed nautilus-sendto plugin (deprecated and broken)
* [nm] Use API instead of GConf to create new connections
* [nm] Enable IPv6 on created connections

### Bugs fixed

* [assistant] Crash (@duganchen)
* [pulseaudio] Support for audio profiles
* Generic disconnect method did not work
* Content of dhcpd configuration file after blueman section was removed

## 1.99.alpha2

### New features

* [docs] Add FAQ file and install doc files (@rworkman / Robby Workman)
* [sendto] Add sendto integration for Thunar (@GreenLunar)
* [sendto] Make thunar sendto integration optional (@rworkman / Robby Workman)
* Add optional settings manager integration with Xfce and MATE
  (@rworkman / Robby Workman)
* [nm] Add support for NetworkManager 0.9 / 1.0 to NMPANSupport
* [bluez] Implement keyboard pairing support
* [nm] Add support for ModemManager 1.x to NMPANSupport
* [plugins] Add GameControllerWakelock plugin (@bwRavencl / Matteo Hausner)
* Add blueman-report to create commented logs for bug reports
* [bluez] BlueZ 5 support for audio, serial, recent connections, and setup
  assistant
* Use Gsettings for configuration storage and remove the config plugin system.

### Changes

* [obex] Switch to obexd for sending files
* [browse] Use system's default browser for obex URI if no browse command is set
* [pulseaudio] Make blueman-applet run if pulseaudio is not available
* [ui] Re-implment menu icons
* [ui] Replace / remove deprecated icon names (@Teknocrat / Harvey Mittens)
* [ui] Drop status icon customization (@Teknocrat / Harvey Mittens)
* Drop HAL Support (@rworkman / Robby Workman)
* [configure] Rename --enable-sendto to --enable-nautilus-sendto
  (@rworkman / Robby Workman)
* Fix compatility with Fedora's dbus-python package
* Remove settings for local audio services
* Add function to rename known devices

### Bugs fixed

* [ui] Make some UI elements expand again (@infirit / Sander Sweers)
* Fix crash in PluginManager (Martín Ferrari)
* Avoid crash in transfer service setup dialog
* Make blueman-applet respond to SIGTERM (@Teknocrat / Harvey Mittens)
* Allow setting friendly adapter name in BlueZ 5
* Look for both dhcpd and dhcpd3 and add sbin paths (@infirit / Sander Sweers)
* [libblueman] Fix memory leak (@monsta)
* [libblueman] Add missing includes (@posophe)
* [ui] Move some icons to pixmaps directory (@rworkman / Robby Workman)
* [ui] Fix fallback for notification daemons not capable to handle actions
* [ui] Fix "Shared Folder" widget in Transfer plugin.
* [ui] Fix service disconnect icons
* Do not translate polkit vendor (@pwithnall / Philip Withnall)

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
