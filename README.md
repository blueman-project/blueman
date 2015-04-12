## Description

Blueman is a GTK+ Bluetooth Manager

Blueman is designed to provide a simple yet effective means for
controlling BlueZ API and simplifying bluetooth tasks such as:

* Connecting to 3G/EDGE/GPRS via dial-up
* Connecting to/Creating bluetooth networks
* Connecting to input devices
* Connecting to audio devices
* Sending/Receiving/Browsing files via OBEX
* Pairing

It is lightweight, easy to use, Python based, and GPL licensed.

The original project page of Valmantas Palikša can be found [here](https://launchpad.net/blueman).
Please use the GitHub issue tracker for bugs and questions.

## Dependencies

### Generic dependencies

* [BlueZ 4](http://www.bluez.org/) (>= 4.61)
* [dbus](http://www.freedesktop.org/wiki/Software/dbus/)
* [dbus-python](http://www.freedesktop.org/wiki/Software/DBusBindings/#python)
* [GLib 2](http://www.gtk.org/) (>= 2.32)
* [GTK+ 3](http://www.gtk.org/)
* [gnome-icon-theme](https://git.gnome.org/browse/adwaita-icon-theme/) or [mate-icon-theme](https://github.com/mate-desktop/mate-icon-theme)
* [libappindicator](https://launchpad.net/libappindicator) (optional)
* [notification-daemon](https://git.gnome.org/browse/notification-daemon) or any desktop specific replacement
* [libnotify](https://git.gnome.org/browse/libnotify)
* [obexd](http://www.bluez.org/) (>= 0.47) for sending files
* [obex-data-server](http://wiki.muiline.com/obex-data-server) (>= 0.4.3) for receiving files
* [pulseaudio](http://www.freedesktop.org/wiki/Software/PulseAudio/) (optional)
* [PyGObject](https://wiki.gnome.org/PyGObject)
* [Python](http://www.python.org/) (2.7 or >= 3.2)
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

See the [Wiki page for information about packaged versions of blueman](https://github.com/blueman-project/blueman/wiki/Packaged-versions).

## Support / Troubleshooting

If you're reporting a bug, please read the [Troubleshooting page](https://github.com/blueman-project/blueman/wiki/Troubleshooting) to provide all relevant information.

Feel free to [open a GitHub issue](https://github.com/blueman-project/blueman/issues/new) for anything you need help with.

You can also ask questions or join discussions at [the blueman mailing list](http://ml.mate-desktop.org/listinfo/blueman).

## Contributing

Fork, make your changes, and issue a pull request. If you just want to edit a single file, GitHub will guide you through that process.

### Translate

Translations are managed with transifex.
Go to [transifex blueman project page](https://www.transifex.com/projects/p/MATE/resource/blueman/).
