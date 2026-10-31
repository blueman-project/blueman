# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Blueman Next is a fork of [Blueman](https://github.com/blueman-project/blueman), the GTK 3 / Python Bluetooth manager on top of BlueZ. The `feature/redesign` work modernizes the **manager UI** (cards, inspector, themes) while keeping the existing GTK/GObject/BlueZ architecture. Do not rewrite it in another toolkit or replace the BlueZ backend.

## Workflow rules from INSTRUCTIONS.md

`INSTRUCTIONS.md` is the cross-agent task tracker (Task Board, Active Task, Handoff). It is the single source of truth for AI continuity:
- Read it before changing code. Update only its relevant sections (task status, verification results, handoff) as you work. Don't create other AI tracking files.
- Use stable task IDs (`T-0NN`). Report test status exactly: not run, passed, failed, or blocked.
- Commit each finished phase or verified slice before starting the next one.
- Current priority: the visual redesign first. Existing bugs (`BUG_AUDIT.md`, `BUGS_LOGS.md`) are deferred. Do not edit `BUGS_LOGS.md`.

Background docs: `CLIXAD.md` (original redesign brief), `IMPLEMENTATION_PLAN.md` (phased plan, R-slices), `ARCHITECTURE_AUDIT.md`.

## Commands

```sh
./blueman-next                 # install missing apt deps, meson build into build-local/, run manager from source
./blueman-next --no-deps       # skip apt dependency install
./blueman-next --build-only    # configure + compile only
./blueman-next -- --loglevel DEBUG   # args after -- go to blueman-manager
```
The launcher never installs anything. It copies the generated `build-local/Constants.py` into `blueman/Constants.py` (gitignored) and runs `tools/run-local-manager.py` with `BLUEMAN_SOURCE=1`. That variable makes `Constants.py` resolve UI, icon and theme paths from `data/` in the checkout.

Tests use stdlib `unittest`, and the C extension `_blueman` must be on `PYTHONPATH`. After `./blueman-next --build-only`:
```sh
BLUEMAN_SOURCE=1 PYTHONPATH=build-local/module python3 -m unittest                                  # all
BLUEMAN_SOURCE=1 PYTHONPATH=build-local/module python3 -m unittest test.gui.manager.test_device_cards  # one module
BLUEMAN_SOURCE=1 PYTHONPATH=build-local/module python3 -m unittest test.gui.manager.test_device_cards.<Class>.<test>
```
CI (`.github/workflows/check.yml`) builds `module/` with Autotools and runs `PYTHONPATH=module/.libs python3 -m unittest`.

Lint and type checks, as CI runs them:
```sh
python3 -m flake8                                   # config in .flake8, max line length 120, `_` builtin
MYPYPATH=stubs python3 -m mypy -p blueman --strict   # local GI stubs live in stubs/
```

## Build system

There are two build systems, and both must stay in sync:
- **Meson** (`meson.build`) installs the whole `blueman/` package with `install_subdir`. A new `.py` file is picked up automatically. A new **subpackage** needs its `Makefile.am` added to the `blueman_makefiles` exclude list.
- **Autotools** (`configure.ac`, `Makefile.am`) lists every Python file explicitly. A new module must be added to its directory's `Makefile.am` `*_PYTHON` list. A new directory needs a `Makefile.am`, an entry in the parent `SUBDIRS`, and an entry in `configure.ac`'s `AC_CONFIG_FILES`.
- Data files (themes, icons, UI) follow the same rule. For example, `data/themes/` has both a `meson.build` and a `Makefile.am`.
- The app name and other user-facing identity live in `data/branding.json`, which both build systems read (see `docs/BRANDING.md`). Do not rename compatibility identifiers: the `blueman` package and executables, `org.blueman.*` D-Bus and GSettings IDs, plugin class names, and systemd units.

## Architecture

- **Executables**: `apps/*.in` are templates for `blueman-manager`, `-applet`, `-tray`, `-sendto`, `-services`, `-adapters`, plus the libexec `-mechanism` (root D-Bus service) and `-rfcomm-watcher`. Each is a thin entry point into `blueman/main/`.
- **BlueZ layer** (`blueman/bluez/`): GDBus proxy wrappers (`Adapter`, `Device`, `Manager`, `obex/`). All Bluetooth access goes through these.
- **Plugin system** (`blueman/main/PluginManager.py`, `blueman/plugins/BasePlugin.py`): plugins are discovered as subclasses of `AppletPlugin`, `ManagerPlugin`, `MechanismPlugin` or `ServicePlugin`. Class attributes (`__depends__`, `__conflicts__`, `__priority__`, `__autoload__`, `__gsettings__`) control loading. The applet holds most features (`plugins/applet/`). Manager plugins (`plugins/manager/`) add device-menu items, and the redesigned cards and inspector must keep showing those items.
- **Manager** (`blueman/main/Manager.py`, class `Blueman`): the main window. It owns `ManagerDeviceList` (the original `GenericList`/`DeviceList` TreeView model, still the data source) and the redesign layers in `blueman/gui/manager/`:
  - `ManagerWindow.py`: three-panel shell (sidebar / dashboard / inspector) built with nested `Gtk.Paned`.
  - `ManagerDeviceCards.py`: card view fed from the device list model through immutable `DeviceCardSnapshot`s. Devices are grouped into Connected/Paired/Available, with local search (Ctrl+K) and the discovery radar. Card actions are emitted as `action-requested` with explicit object paths and handled in `Manager.py`.
  - `ManagerDeviceInspector.py`: details panel bound to the selected card.
  - `ManagerSettings.py`: settings dialog exposing only existing GSettings keys from `data/org.blueman.gschema.xml`.
  - The classic TreeView remains as a compatibility fallback.
- **Theming** (`blueman/gui/theme/`): `ThemeManager` singleton loads `data/themes/{dark,light}.css` as GTK CSS providers. `system` mode resolves to light or dark from the desktop but still applies the Blueman Next palette. `DesignTokens.py` and `AnimationManager.py` hold the shared tokens and reduced-motion handling.
  - Both stylesheets are **generated** by `tools/generate-themes.py` (per-theme palette tokens plus one shared rule set). Edit the generator and rerun it; never hand-edit the CSS.
  - Use GTK ≥3.20 CSS node names (`switch`, `row`, `entry`, `paned > separator`); `GtkXxx` type selectors are silently ignored.
  - Surfaces must stay opaque: GTK 3 has no blur, and translucency shows other windows through. Don't call `set_app_paintable(True)` on the window, since it suppresses the CSS background.
- **Window chrome**: the manager uses an empty titlebar widget (CSD with no header strip), custom traffic-light buttons in the sidebar, and drag areas (`_drag_area` in `ManagerWindow.py`). Responsive breakpoints are measured on `main_paned` (content), not the toplevel (which includes CSD shadow margins). Side panes are packed `shrink=True` so the window's minimum size stays below the compact breakpoints.
- **C extension** (`module/_blueman.pyx`, Cython): low-level helpers (rfcomm, conn info). It is built into `build-local/module/`.

## Redesign constraints

- Show only real data: no invented battery, signal, or transfer values. Leave out measurements that aren't known.
- Don't change pairing/agent control flow (`BluezAgent`, `AuthAgent`) or OBEX semantics while redesigning their UI.
- Timers and animations exist only while a widget is mapped and active, and they respect reduced motion.
- Manager GUI tests live in `test/gui/manager/` and use fake device lists, not D-Bus. Add tests there for new UI behavior.
- The distribution applet may be older than this checkout (e.g. 2.3.5 advertises `PowerManager` but does not export its interface). Power state falls back to the adapter's `Powered` property; keep D-Bus calls to the applet guarded.
- `test.main` D-Bus tests need `python-dbusmock`; flake8 and mypy may not be installed system-wide.
