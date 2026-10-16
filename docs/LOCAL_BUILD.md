# Local build without installation

Use the repository launcher to configure, compile, and run Blueman Next
without replacing the distribution-provided Blueman:

```sh
./blueman-next
```

The command builds into the ignored `build-local/` directory and runs the
manager directly from the checkout. It never runs `meson install`, writes to
system directories, or changes the official `blueman` executable.

The build dependencies listed in [`Dependencies.md`](../Dependencies.md) must
already be available. The launcher deliberately does not install missing
packages; Meson will report the dependency that needs to be provided.

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
