# Dependencies

## Runtime dependencies

* [BlueZ 5](http://www.bluez.org/)
* [dbus](http://www.freedesktop.org/wiki/Software/dbus/)
* [GdkPixbuf](http://www.gtk.org/) (GI bindings)
* [GLib 2, Gio 2](http://www.gtk.org/) (>= 2.32) (GI bindings)
* [GTK+ 3](http://www.gtk.org/) (GI bindings) [1]
* [gnome-icon-theme](https://git.gnome.org/browse/adwaita-icon-theme/), [mate-icon-theme](https://github.com/mate-desktop/mate-icon-theme), [adwaita-icon-theme](https://github.com/GNOME/adwaita-icon-theme), [elementary-xfce](https://github.com/shimmerproject/elementary-xfce), or [Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)
* [libappindicator](https://launchpad.net/libappindicator) (optional) (GI bindings)
* [notification-daemon](https://developer.gnome.org/notification-spec/) that provides dbus name org.freedesktop.Notifications
* [obexd 5](http://www.bluez.org/)
* [Pango](http://www.gtk.org/) (GI bindings)
* [pulseaudio](http://www.freedesktop.org/wiki/Software/PulseAudio/) (optional; its bluetooth module is required to actually use audio devices)
* [pycairo](http://cairographics.org/pycairo/)
* [PyGObject 3](https://wiki.gnome.org/PyGObject) (>= 3.27.2)
* [Python](http://www.python.org/) (>= 3.3)
* [net-tools](http://net-tools.sourceforge.net/) for blueman 2.0 and net-tools __or__ [iproute2](https://wiki.linuxfoundation.org/networking/iproute2) for blueman 2.1
* [libnm](https://wiki.gnome.org/Projects/NetworkManager) For managing DUN and PANU connection (GI bindings)

## Build dependencies

* [BlueZ 5](http://www.bluez.org/)
* [Cython](http://www.cython.org/)
* [GLib 2](http://www.gtk.org/) (>= 2.32)
* [intltool](http://freedesktop.org/wiki/Software/intltool/)
* [libtool](http://www.gnu.org/software/libtool/)
* [PyGObject 3](https://wiki.gnome.org/PyGObject) (>= 3.27.2)
* [Python](http://www.python.org/) (>= 3.3)

## Additional dependencies for VCS version

* [autogen](https://www.gnu.org/software/autogen/)
* [automake](https://www.gnu.org/software/automake/)
* [autoconf](https://www.gnu.org/software/autoconf/)

[1] There is a known issue with GTK+ <= 3.10.6, possibly in conjuction with specific themes or similar conditions. If it is present and a message is to be displayed in blueman-manager's message area the application will crash with

    Gtk-CRITICAL **: gtk_style_context_get_property: assertion ``priv->widget != NULL || priv->widget_path != NULL' failed
