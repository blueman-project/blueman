# Dependencies

## Generic dependencies

* [BlueZ 4](http://www.bluez.org/) (>= 4.61)
* [dbus](http://www.freedesktop.org/wiki/Software/dbus/)
* [dbus-python](http://www.freedesktop.org/wiki/Software/DBusBindings/#python)
* [GLib 2, Gio 2](http://www.gtk.org/) (>= 2.32)
* [GTK+ 3](http://www.gtk.org/) [1]
* [gnome-icon-theme](https://git.gnome.org/browse/adwaita-icon-theme/) or [mate-icon-theme](https://github.com/mate-desktop/mate-icon-theme)
* [libappindicator](https://launchpad.net/libappindicator) (optional)
* [notification-daemon](https://git.gnome.org/browse/notification-daemon) or any desktop specific replacement
* [libnotify](https://git.gnome.org/browse/libnotify)
* [obexd](http://www.bluez.org/) (>= 0.47)
* [pulseaudio](http://www.freedesktop.org/wiki/Software/PulseAudio/) (optional)
* [PyGObject 3](https://wiki.gnome.org/PyGObject)
* [Python](http://www.python.org/) (2.7 or >= 3.2)

## Additional build dependencies

* [libtool](http://www.gnu.org/software/libtool/)
* [intltool](http://freedesktop.org/wiki/Software/intltool/)
* [Cython](http://www.cython.org/)

## Additional dependencies for VCS version

* [autogen](https://www.gnu.org/software/autogen/)
* [automake](https://www.gnu.org/software/automake/)
* [autoconf](https://www.gnu.org/software/autoconf/)

[1] There is a known issue with GTK+ <= 3.10.6, possibly in conjuction with specific themes or similar conditions. If it is present and a message is to be displayed in blueman-manager's message area the application will crash with

    Gtk-CRITICAL **: gtk_style_context_get_property: assertion ``priv->widget != NULL || priv->widget_path != NULL' failed
