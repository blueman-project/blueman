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
* [GTK+ 3](http://www.gtk.org/)
* [libappindicator](https://launchpad.net/libappindicator) (optional)
* [notification-daemon](https://git.gnome.org/browse/notification-daemon) or any desktop specific replacement
* [libnotify](https://git.gnome.org/browse/libnotify)
* [obexd](http://www.bluez.org/) for sending files
* [obex-data-server](http://wiki.muiline.com/obex-data-server) (>= 0.4.3) for receiving files
* [pulseaudio](http://www.freedesktop.org/wiki/Software/PulseAudio/)
* [PyGObject](https://wiki.gnome.org/PyGObject)
* [Python 2.7](http://www.python.org/)
* [startup-notification](http://www.freedesktop.org/wiki/Software/startup-notification/)

### Additional build dependencies

* [libtool](http://www.gnu.org/software/libtool/)
* [intltool](http://freedesktop.org/wiki/Software/intltool/)
* [Cython](http://www.cython.org/)

### Additional dependencies for VCS version

* [autogen](https://www.gnu.org/software/autogen/)
* [automake](https://www.gnu.org/software/automake/)
* [autoconf](https://www.gnu.org/software/autoconf/)

## Installing

To install a packaged release of blueman, run `./configure && make && make install`.

To generate and run a configure script from source, run `./autogen.sh`.

## Packaged versions

* [Arch Linux](https://aur.archlinux.org/packages/blueman/)
* [Debian GNU/Linux](http://packages.debian.org/search?keywords=blueman)
* [Gentoo Linux](http://packages.gentoo.org/package/net-wireless/blueman)
* Linux Mint
* OpenMandriva
* [openSUSE](http://software.opensuse.org/package/blueman?search_term=blueman)
* [Ubuntu](http://packages.ubuntu.com/search?keywords=blueman)

## Support / Troubleshooting

Feel free to [open a GitHub issue](https://github.com/blueman-project/blueman/issues/new) for anything you need help with. If you're reporting a bug, please read the [Troubleshooting page](https://github.com/blueman-project/blueman/wiki/Troubleshooting) to provide all relevant information.

## Contributing

Fork, make your changes, and issue a pull request. If you just want to edit a single file, GitHub will guide you through that process.

### Translate

Translations are managed with transifex.
Go to [transifex blueman project page](https://www.transifex.com/projects/p/MATE/resource/blueman/).
