The original blueman project of Valmantas Palikša can be found [here](https://launchpad.net/blueman). The latest stable version is 1.23 released in Oct. 2011.

We're currently working on blueman 2 to bring support for newer APIs like BlueZ 5 and NetworkManager 0.9. Any contributions are welcome.

## Dependencies

### Generic dependencies

* [BlueZ 4](http://www.bluez.org/) (>= 4.25)
* [dbus](http://www.freedesktop.org/wiki/Software/dbus/)
* [dbus-python](http://www.freedesktop.org/wiki/Software/DBusBindings/#python)
* [GTK+ 2](http://www.gtk.org/) (>= 2.16)
* [libappindicator](https://launchpad.net/libappindicator) (optional)
* [notification-daemon](http://galago-project.org/)
* [notify-python](http://galago-project.org/)
* [obex-data-server](http://wiki.muiline.com/obex-data-server) (>= 0.4.3)
* [pulseaudio](http://www.freedesktop.org/wiki/Software/PulseAudio/)
* [PyGObject](https://wiki.gnome.org/PyGObject)
* [PyGTK](http://www.pygtk.org/) (>= 2.16)
* [Python 2](http://www.python.org/) (>= 2.5)
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

To install a packaged release of blueman, run ./configure, make and make install.

To generate and run a configure script from from source, run ./autogen.sh. You can provide configuration options to the autogen.sh script.

## Binaries

Binary versions of blueman 1 are available for the following systems:

* [Arch Linux](https://www.archlinux.org/packages/?name=blueman)
* CentOS
* [Debian GNU/Linux](http://packages.debian.org/search?keywords=blueman)
* [Fedora](https://apps.fedoraproject.org/packages/blueman)
* Linux Mint
* [Mageia](http://mageia.madb.org/package/show/name/blueman)
* [openSUSE](http://software.opensuse.org/package/blueman?search_term=blueman)
* [Ubuntu](http://packages.ubuntu.com/search?keywords=blueman)
