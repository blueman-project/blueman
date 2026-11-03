# Local build without installation

Use the repository launcher to configure, compile, and run Blueman Next
without replacing the distribution-provided Blueman:

```sh
./blueman-next
```

The command builds into the ignored `build-local/` directory and runs the
manager directly from the checkout. It never runs `meson install`, writes to
system directories, or changes the official `blueman` executable.

On Debian and Ubuntu, the launcher checks the required build/runtime packages
and uses `apt-get` (through `sudo` when needed) to install only those that are
missing. This installs development dependencies, not the Blueman application,
and may ask for the user's sudo password. Package installation can be disabled
for offline or pre-provisioned environments:

```sh
./blueman-next --no-deps
```

Other distributions should install the packages listed in
[`Dependencies.md`](../Dependencies.md), then use `--no-deps`.

To compile without launching the manager:

```sh
./blueman-next --build-only
```

Manager arguments can be passed after `--`:

```sh
./blueman-next -- --loglevel DEBUG
```

Use a different build directory by setting `BLUEMAN_BUILD_DIR` to an absolute
path or a path relative to the repository root.

The launcher cannot be named `./blueman` because that path is already the
Python package directory in this repository. `./blueman-next` is the local,
non-conflicting equivalent.
