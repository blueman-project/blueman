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

The original project page of Valmantas Palikša can be found [on Launchpad](https://launchpad.net/blueman).
Please use the GitHub issue tracker for bugs and questions.

## Installing

See [Dependencies.md](Dependencies.md) for a list of build and runtime dependencies.

To install a packaged release of blueman, run `./configure && make && make install`.

To generate and run a configure script from source, run `./autogen.sh`.

If you are packaging it for your distribution please make sure to pass `--disable-schemas-compile` and run `glib-compile-schemas /datadir/glib-2.0/schemas` as part of your (un)install phase.

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
