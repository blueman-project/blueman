## Description

Blueman is a GTK+ Bluetooth Manager

Blueman is designed to provide simple, yet effective means for
controlling BlueZ API and simplifying bluetooth tasks such as:

* Connecting to 3G/EDGE/GPRS via dial-up
* Connecting to/Creating bluetooth networks
* Connecting to input devices
* Connecting to audio devices
* Sending/Receiving/Browsing files via OBEX
* Pairing

It is lightweight, easy to use, Python bases and GPL licensed.

The original project page of Valmantas Palikša can be found [here](https://launchpad.net/blueman).
Please use the GitHub issue tracker for bugs and questions.

## Roadmap

The latest stable version is 1.23 released in Oct. 2011.

Blueman 2 will especially bring support for newer APIs like BlueZ 5 and NetworkManager 0.9 and fix a number of issues.

## Dependencies

### Generic dependencies

* [BlueZ 4](http://www.bluez.org/) (>= 4.61)
* [dbus](http://www.freedesktop.org/wiki/Software/dbus/)
* [dbus-python](http://www.freedesktop.org/wiki/Software/DBusBindings/#python)
* [GLib 2](http://www.gtk.org/) (>= 2.32)
* [GTK+ 2](http://www.gtk.org/) (>= 2.16)
* [libappindicator](https://launchpad.net/libappindicator) (optional)
* [notification-daemon](http://galago-project.org/)
* [notify-python](http://galago-project.org/)
* [obex-data-server](http://wiki.muiline.com/obex-data-server) (>= 0.4.3)
* [pulseaudio](http://www.freedesktop.org/wiki/Software/PulseAudio/)
* [PyGObject](https://wiki.gnome.org/PyGObject)
* [PyGTK](http://www.pygtk.org/) (>= 2.16)
* [Python 2](http://www.python.org/) (>= 2.6)
* [startup-notification](http://www.freedesktop.org/wiki/Software/startup-notification/)

### Additional build dependencies

* [libtool](http://www.gnu.org/software/libtool/)
* [intltool](http://freedesktop.org/wiki/Software/intltool/)
* [Pyrex](http://www.cosc.canterbury.ac.nz/greg.ewing/python/Pyrex/)

### Additional dependencies for VCS version

* [autogen](https://www.gnu.org/software/autogen/)
* [automake](https://www.gnu.org/software/automake/)
* [autoconf](https://www.gnu.org/software/autoconf/)

## Installing

To install a packaged release of blueman, run `./configure && make && make install`.

To generate and run a configure script from source, run `./autogen.sh`.

## Packaged versions

Development snapshots of blueman 2:

* [Arch Linux](https://www.archlinux.org/packages/?name=blueman)
* [Debian GNU/Linux](http://packages.debian.org/search?keywords=blueman)
* [Ubuntu](http://packages.ubuntu.com/search?keywords=blueman)

Older versions:

* CentOS
* [Fedora](https://apps.fedoraproject.org/packages/blueman)
* [Gentoo Linux](http://packages.gentoo.org/package/net-wireless/blueman)
* Linux Mint
* [Mageia](http://mageia.madb.org/package/show/name/blueman)
* [openSUSE](http://software.opensuse.org/package/blueman?search_term=blueman)

## Contributing

Fork, make your changes and issue a pull request. If you just want to edit a single file
(e.g. translations in the po folder), GitHub will guide you through that process.

### Translate

Translations are managed with transifex.
Go to [transifex blueman project page](https://www.transifex.com/projects/p/MATE/resource/blueman/).
