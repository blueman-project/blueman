# Changelog

## 2.0.8

### Bugs fixed
* Fix name resolution of unknown device classes

## 2.0.7

### Changes

This release fixes DUN support in blueman through NetworkManager and bluemans own implementation with pppd. It has been broken due to lack of hardware as DUN is usually not available on newer devices. We now have an old phone and an Android app to get thing working but we would love to get some feedback if bluemans DUN support works for you or not.

We also added default polkit rules file that allows users in group wheel to perform administrative actions. Note that the administrative group might have a different name (e.g. sudo in the Debian family) and there might be additional groups that are appropriate for the actions (e.g. netdev in the Debian family), so it still makes sense for distributions to adapt the configuration.

Support iproute2 and make it the default

### Bugs fixed
* Fix icon name in the device menu
* Several commits backported from master for various RFCOMM and Serial related bugs.
* Fix icon and caption in manager for LE devices

## 2.0.6

**This release adds authorisation checks for the commands blueman runs as root**

We added the following policykit authorisation checks
* org.blueman.network.setup
* org.blueman.pppd.pppconnect
* org.blueman.rfkill.setstate

See https://github.com/blueman-project/blueman/wiki/PolicyKit

## 2.0.5

### Bugs fixed

* PPPSupport: Correrct binary name for ModemManager
* PPPSupport: Exclude grep process from process list
* GameControllerWakeLock: Check for Class property before using it
* SerialManager: Properly check for None
* NetConf: Treat UnicodeDecodeError as if there was no file
* Notification: Also check if notification daemon supports body
* Correct bold tag in portugese translation (thanks @andreyluiz)
* Properly check for None in SerialManager
* GameControllerWakeLock: Check for Class property first
* Fix bugs in NetworkService ui
* NetConf: fix writing PID file for dhcpd(3)
* Notification: Make sure x and y hint are in screen geometry

## 2.0.4

### Changes

* Do not try to send a file during a discovery

### Bugs fixed

* Listing rfcomm devices was broken
* Serial devices where not properly disconnected
* Close confirmation dialog on cancelation
* Handle transfer errors correctly
* Show devices of the current adapter only
* Local network service did not work
* PyGI warnings
* Call custom scripts for serial services
* Disconnect serial services on device disconnect

## 2.0.3

Fix privilege escalation

## 2.0.2

### Bugs fixed

* Exception on device property change
* Backport fix for #345 - rename random pass pairing button
* Exception at exit (#391)
* Clarify wording of tray applet's option to turn off bluetooth
* Do not block manager with plugin dialog (#383)
* blueman-adapters: Set hidden in the ui when timeout is reached
* Functions: Catch specific error in get_icon function
* Stop Game Controller plugin from blocking
* Use absolute filename provided to blueman-sendto on the cmd line

## 2.0.1

### Bugs fixed

* Codepoint issues when connecting to serial service
* Infinite loop if RecentConns has only invalid items
* Unblock rfkill in Python 3
* Valid adapter may not be found
* Handle when rfkill subsystem is not available gracefully
* RfKill: open /dev/rfkill r+b to avoid creating
* Resolve codepoint issues in several places
* Stop dhcpd handler removing all content of the config file

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
