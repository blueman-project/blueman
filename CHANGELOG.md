# Changelog

## master

### Changes

* Drop support for BlueZ 4
* Drop browse feature
* Add title to status icon
* Add systemd service units (@smcv / Simon McVittie)
* Set widget names so they can be used to style blueman.
* Replace deprecated use of Gtk.VBox and Gtk.HBox.
* Replace deprecated GtkTable with GtkGrid and also use it replace GtkBoxes used to layout.

### Bugs fixed

* Codepoint issues when connecting to serial service
* Infinite loop if RecentConns has only invalid items
* Unblock rfkill in Python 3
* Valid adapter may not be found
* Do not load RfKill plugins when device is not available.
* Always set codeset for gettext to utf8 (@mgorny / Michał Górny)
* Support legacy devices without a Name property
* (Covered) Crash in agent's passkey / pin code methods
* Fix fading in GtkAnimation TreeRow(Color)Fade and CellFade classes.
* Do not explixitely destoy DeviceSelectorDialog blueman-sendto.
* gui: Call the sub-classed widgets init function instead of GObject's

## 2.0

No relevant changes

## 2.0.rc1

### New features

* Support for Python 3
* [dhcp] udhcpc (busybox) support

### Changes

* [ui] Button to reset device alias
* [bluez] Agent capability KeyboardDisplay (@kemnade-uni / Andreas Kemnade)
* New configuration option to disable the use of a notification daemon
* [sendto] Removed nautilus-sendto plugin (deprecated and broken)
* [nm] Use API instead of GConf to create new connections
* [nm] Enable IPv6 on created connections
* Use GAppInfo to launch applications
* [bluez] Auto power on adapters; can be disabled in PowerManager settings
* Remove Gtk+, GLib and Gio as build time dependencies
* [obex] Migrate receiving files from obex-data-server to obexd
* [ui] Plugins and local services items in manager's View menu

### Bugs fixed

* [assistant] Crash (@duganchen)
* [pulseaudio] Support for audio profiles
* Generic disconnect method did not work
* [bluez] Handsfree service crashed with BlueZ 4

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
