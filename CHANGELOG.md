# Changelog

## 2.3.5

### Bugs fixed

* Right click menu was pointing to the wrong list row
* Double click to connect


## 2.3.4

### Bugs fixed

* Errors when connected to a device with the DisconnectItems plugin enabled

## 2.3.3

### Changes

* Do not re-use dbusmenu item identifiers; avoids issues at least with gnome-shell-extension-appindicator.

### Bugs fixed

* Issues with NM PANU connections of equally named devices
* Submenus in KDE Plasma tray
* Avoid using StatusNotifierItem and GtkStatusIcon icons in parallel

## 2.3.2

### Bugs fixed

* StatusNotifierItem submenus did not work in lxqt-panel (@niknah)
* StatusNotifierItem vanished on panel restarts
* StatusNotifierItem compatibility issues with libdbusmenu used at least by xfce4-panel and Waybar
* StatusNotifierItem showed the menu on left click in xfce4-panel

## 2.3.1

### Bugs fixed

* StatusNotifierItem sent an incomplete NewStatus signal.
* Avoid statusbar resize when showing progressbar

## 2.3

### Bugs fixed

* Blocked emblem was not visible for scales other than 1

## 2.3.beta1

### New features

* Audio profile switcher in applet menu (@abhijeetviswa)
* Symbolic tray icon option (GSettings switch symbolic-status-icons in org.blueman.general)

### Changes

* Replace AppIndicator with DBus StatusNotifierItem
* Use a GtkTreeModelFilter to show/hide unnamed devices
* Replace sigint hack with GLib to catch it
* Port meson from deprecated python3 module
* Rework battery handling
* Merge Battery applet plugin into ConnectionNotifier
* Symbolic icons and small UI improvements

## 2.2.5

### Bugs fixed

* Fix network interface iteration on 32 bit systems
* Manager: Fix cancel button in send-note dialog
* Fix battery and signals bars

## 2.2.4

### Changes

* Dropped the PIN database

### Bugs fixed

* blueman-mechanism accepted arbitrary file paths and returned the errors from trying to open them, see https://github.com/blueman-project/blueman/security/advisories/GHSA-3r9p-m5c8-8mw8

## 2.2.3

### Bugs fixed

* Recent connections disabled after suspend and resume
* Service authorization notifications did not respond
* Passkeys did not get displayed

## 2.2.2

### Bugs fixed

* Issues with power level bars
* Error message in blueman-mechanism

## 2.2.1

### Bugs fixed

* Hard dependency of DBusService on NetworkManager

## 2.2

### New features

* Disconnect items in applet menu (plugin)
* Desktop notifications on connect / disconnect (plugin)
* Notifications with battery level for connecting devices (applet plugin)
* Stop discovery and retry connection for broken adapter drivers
* Auto-connect settings for supported services

### Changes

* Drop blueman-report
* Drop blueman-assistant
* Raise minimum Python version to 3.6
* Raise GTK+ 3 version to 3.22
* Raise minimum BlueZ version to 5.48
* Allow opening device menus via keyboard (Shift+F10 or menu key)
* Add Ctrl+Q and Ctrl+W accelerators for closing blueman-manager
* Allow cancelling device connection attempts
* Improved passkey handling (fixed padding, highlighting, single notifitication)
* Hide devices with no name

### Bugs fixed

* Fix disconnecting NMDevice
* Exceptions from asynchronous DBus calls (getting picked up by tools like Apport or ABRT)
* DiscvManager plugin showed its icon unreliably

## 2.1.4

### Changes
* Force cython to use python language version 3
* Do not use exitcode 1 when we expect to fail
* Mark more strings translatable (@cwendling)

### Bugs fixed

* Untranslated strings (@cwendling / Colomban Wendling)
* Searching (with Ctrl+F in manager device list) did not work
* Default PIN lookup
* Fix device removal handling (@Yannik)
* Only use LaunchContext when we have proper event time

## 2.1.3

### Changes
* Use apply button for transfer options

### Bugs fixed
* Fix tooltip not updating when bluetooth is disabled
* Fix dbus timeout in DhcClient
* Call the right method when pulseaudio crashes
* Handle os.remove failing

## 2.1.2

### Bugs fixed

* Signal bar updates with multiple adapters
* Pairing with pincode

## 2.1.1

### Bugs fixed

* Using recent connections did not work
* Switching adapters did not work
* Errors when removing a device
* Error tracebacks from info dialog

## 2.1

### Changes

* New PIN database

### Bugs fixed

* Crash in blueman-manager and blueman-adapters if no adapter is present
* Many issues in blueman-sendto

## 2.1.beta1

### Changes

* Use GDBus and drop dependency on dbus-python
* Small improvements for LE devices
* Removed NetworkManager 0.8 support from NetUsage plugin
* Handle invalid directory for incoming file transfers
* Quit blueman-sendto when no file was selected
* Use build-time python executable for shebangs
* Ask user for initial auto-power-on setting

### Bugs fixed

* Streamlined icon usage so that blueman now supports gnome-icon-theme, mate-icon-theme, adwaita-icon-theme, elementary-xfce, and Papirus
* Handle corrupt network configuration file
* The menu bar did not get updated correctly

## 2.1.alpha3

### Changes

* Added default polkit rules file that allows users in group wheel to perform administrative actions
* Use context managers for opening files
* Replace deprecated os.popen with subprocess
* Reimplement NetworkManager integration for DUN and PANU connection with libnm
* Disable DNS on dnsmasq
* Avoid authorization check
* Use GtkWindow for instead of a GtkDialog when there is no parent
* Stop using and remove TimeHint

### Bugs fixed

* RFCOMM channel detection for DUN service failed
* Fix DUN support though blueman and NetworkManager. We love to get feedback if this works for people
* Use correct name network-transmit-receive for icon (ManagerDeviceMenu)
* For a few GLib warning related to signals in ManagerDeviceMenu
* Fix Generic connect not showing in certain situations
* Many fixes in PPPSupport and PPPConnection
* Wait for Modemmanager longer to finnish probing a bluetooth modem
* Fix iconname typo in ErrorDialog
* Use returncode to check if DhcpdHandler started correctly

## 2.1.alpha2

### New features

* blueman-adapters is now (Xfce-)pluggable
* Allow users to copy data from the Info manager plugin
* Add connman support to KillSwitch plugin
* Implement a new standalone tray app
* Add support for HiDPI in the UI
* Add command line option to blueman-mechanism to stop timer
* Add support for, and prefer, the ip command to configure network devices
* Implement new plugin virtual on_delete function using weakref.finalize

### Changes

* Show "Proprietary" instead of "Unknown" for services with non-reserverd UUIDs
* Generic connect and disconnect
* blueman-services: rework dhcpd handler radio buttons
* Implement a ServiceUUID class
* invoke _NotificationDialog.callback with 1 argument (@dakkar)
* Drop support for Python 2.7
* RecentConns: Store items in a gsettings array of dict
* Migrate from EventBox to InfoBar
* Reintroduce GtkImageMenuItem
* Sendto: Replace progressbar with spinner and always discover
* Add a generic ErrorDialog combining various dialogs classes
* ManagerDeviceMenu: set certain setvice insensitive when not paired
* ManagerDeviceList: Only update signal levels if they changed
* Drop unused obex.Errors
* Use GObjectMeta to handle singleton in out BlueZ classes
* Various UI cleanups
* Remove various python2/3 compatibility workarounds

### Bugs fixed

* Icon disappeared when switching off bluetooth
* Revert "bluez manager: Subclass from GDBusObjectManagerClient"
* Icon briefly vanished when turning on bluetooth
* Fix DBus signal emission
* blueman-services: Fix radio button group
* Fix InfoBar animation
* Fix Drag&Drop in blueman-manager
* Use Appearance device property for bluetooth LE devices
* AppIndicator: Properly set title on indicator
* Implement function to retrieve rfcomm channel (serial devices)
* TransferService: Do not unregister when dbus name disappears
* Fix Obexd autostart in our BlueZ classes
* Properly update ui when unblocking adapter with rfkill


## 2.1.alpha1

### New features

* Information dialog on device's services
* Compose vNotes
* --delete option for blueman-sendto

### Changes

* Drop support for BlueZ 4
* Drop browse feature
* Add title to status icon
* Add systemd service units (@smcv / Simon McVittie)
* Set widget names so they can be used to style blueman.
* Replace deprecated use of Gtk.VBox and Gtk.HBox.
* Replace deprecated GtkTable with GtkGrid and also use it replace GtkBoxes used to layout.
* [dhcp] udhcpd (busybox) support
* [sendto] Do not try to send a file during a discovery
* Migrate the BlueZ classes from dbus-python to GDBus
* Limit who can run blueman's mechanism with polkit
* Use GtkListStore builtin sorting functionality
* Turn the BlueZ classes into singletons
* Update Sdp class id's
* Rework Adapter menu in ManagerMenu
* Rework and cleanup DeviceList class
* Drop headset service and plugin
* Merge the two property changed functions in PropertiesBase
* Remove main.Device
* Fix building with musl libc
* Add generic device-added/removed functions for plugins
* Drop legacy NetworkManager and ModemManager support
* Port AppletService proxy to GDBus
* Port Polkit client code to GDBus
* [ManagerDeviceMenu] Make disconnecting and opening plugin dialog asynchronous operations
* Implement default pin (RequestPinCode) database for BluezAgent
* Bluez, Subclass from Gio.DBusProxy and properly handle properties
* Bluez managers, Subclass from GDBusObjectManagerClient
* Notification: Use dbus for notifications and drop the libnotify dep
* Port NMPanSupport applet plugin to GDBus
* Open rfcomm device as unprivileged user if he has read and write access


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
* Do not block manager with plugin dialog
* Exception in Tee class at exit
* Stop dhcpd handler removing all content of the config file
* Only return devices belonging to adapter
* Fix SerialManager plugin
* Close Notification when pair is successful
* Properly unregister NAP when unloading Networking plugin
* PPPSupport: Wait for ModemManager to complete probing and release the device

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
