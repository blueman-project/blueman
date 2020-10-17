## Description

Blueman is a GTK+ Bluetooth Manager

Blueman is designed to provide a simple yet effective means for
controlling the BlueZ API and simplifying Bluetooth tasks, such as:

* Connecting to 3G/EDGE/GPRS via dial-up
* Connecting to / Creating Bluetooth networks
* Connecting to input devices
* Connecting to audio devices
* Sending / Receiving files via OBEX
* Pairing

It is lightweight, easy to use, Python based, and GPL licensed.

The original project page of Valmantas Palikša can be found [on Launchpad](https://launchpad.net/blueman).

## Installing

See [Dependencies.md](Dependencies.md) for a list of build and runtime dependencies.

To install a packaged release of blueman, run `./configure && make && make install`.

To generate and run a configure script from source, run `./autogen.sh`.

If you are packaging it for your distribution, please make sure to pass `--disable-schemas-compile` and run `glib-compile-schemas /datadir/glib-2.0/schemas` as part of your (un)install phase.

## Packaged versions

The [wiki page has info about packaged versions of blueman](https://github.com/blueman-project/blueman/wiki/Packaged-versions).

## Support / Troubleshooting

If you're reporting a bug, please read the [Troubleshooting page](https://github.com/blueman-project/blueman/wiki/Troubleshooting) to provide all relevant info.

Feel free to [open a GitHub issue](https://github.com/blueman-project/blueman/issues/new) to file bugs, or ask about anything you need help with.

## Contributing

Fork, make your changes, and issue a pull request. If you just want to edit a single file, GitHub will guide you through that process.

### Translate

Translations are managed on Hosted Weblate.
Go to the [Weblate blueman project page](https://hosted.weblate.org/projects/blueman/).

## License

All parts of the software are licensed under GPLv3 (or GPLv2) and allow redistribution under any later version.
