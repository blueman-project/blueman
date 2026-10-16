# Blueman Next — Architecture Audit (Phase 0)

Scope: local fork at `/home/dorin/work/nirodg/blueman`, version 2.4.3, branch `main`.
Revision: 2026-10-15, commit `67cea9010c114f1fd9df966d52a53b0a7f68f47f`.
No production code was modified. This is a static architecture assessment with an
unconfigured test attempt; hardware behavior is not certified. Existing bug fixes
remain deferred until after the redesign, per the user’s explicit priority.

## 1. Framework and language

| Item | Finding | Evidence |
|---|---|---|
| GTK | **GTK 3** (`gi.require_version("Gtk", "3.0")` in every GUI module) | `blueman/main/Manager.py:32`, `blueman/gui/*.py`, `blueman/plugins/**` |
| Python | **3.11+ required** by meson; dev box runs 3.12.3 | `meson.build:18` |
| GObject bindings | PyGObject 3.48.2 on the dev box | `python3 -c "import gi"` |
| D-Bus client | **Gio.DBusProxy** (no dbus-python / pydbus) | `blueman/bluez/Base.py:49`, `blueman/main/DBusProxies.py:17` |
| Stylesheets | **None.** No `.css` file and no `Gtk.CssProvider` anywhere in the repo | glob `**/*.css` returns nothing |
| UI definitions | 15 `.ui` files in `data/ui/`, loaded via `blueman/main/Builder.py` (`class Builder(Gtk.Builder)`) | `data/ui/*.ui` |
| Main window | `Gtk.ApplicationWindow` (`manager_window`) with `GtkToolbar` (`toolbar`), `GtkInfoBar` (`message_area`) and a status bar; **no HeaderBar, no Paned, no Stack** | `data/ui/manager-main.ui:267,384,445` |

Conclusion: the framework fits the brief (GTK 3, Builder, Gio/GLib). The brief's
"Gtk.Stack / Gtk.HeaderBar / Gtk.Paned" targets are all absent today, so the window
redesign is a real rewrite of `manager-main.ui` and `Manager.py`, not a restyle.
Because there is no CSS yet, the design-system work starts from zero.

## 2. Entry points

| Entry | Path | Notes |
|---|---|---|
| Manager (main window) | `blueman/main/Manager.py` — `class Blueman(Gtk.Application)`, app id `org.blueman.Manager` | Creates `AppletService` and `AppletPowerManagerService` proxies; exits with `DBusProxyFailed` if the applet is not running (`Manager.py:61`) |
| Applet / tray | `blueman/main/Applet.py`, `blueman/main/Tray.py` | Tray backends: `indicators/GtkStatusIcon.py`, `indicators/StatusNotifierItem.py` |
| Send-to | `blueman/main/Sendto.py`, `sendto/` | Thunar/Nautilus integration via `data/thunar-sendto-blueman.desktop.in` |
| Services | `blueman/main/Services.py` | Service window, uses `services-window.ui` |
| Adapters | `data/blueman-adapters.desktop.in` | Adapter selection dialog |
| Desktop files | `data/blueman.desktop.in`, `data/blueman-manager.desktop.in`, `data/blueman-adapters.desktop.in` | Display name is hard-coded here |

## 3. Bluetooth manager architecture

```
Manager (Gtk.Application)  blueman/main/Manager.py
 ├─ Builder("manager-main.ui")          data/ui/manager-main.ui
 ├─ PluginManager(ManagerPlugin, blueman.plugins.manager)
 │    └─ manager plugins: Info, Notes, PulseAudioProfile, Services, …
 ├─ ManagerDeviceList   blueman/gui/manager/ManagerDeviceList.py (677 lines)
 │    └─ builds on blueman/gui/DeviceList.py and GenericList.py (Gtk.TreeView based)
 ├─ ManagerToolbar      blueman/gui/manager/ManagerToolbar.py
 ├─ ManagerMenu         blueman/gui/manager/ManagerMenu.py
 ├─ ManagerDeviceMenu   blueman/gui/manager/ManagerDeviceMenu.py (453 lines)
 ├─ ManagerStats        blueman/gui/manager/ManagerStats.py
 └─ ManagerProgressbar  blueman/gui/manager/ManagerProgressbar.py
```

The device list is a **TreeView** (`GenericList` / `DeviceList`), not a ListBox. The backing model is a `Gtk.ListStore` with a `Gtk.TreeModelFilter`;
`DeviceList.path_to_row` maps BlueZ object paths to `Gtk.TreeRowReference`.
`get()` returns dictionaries of requested column values. Address is device data,
not the primary row lookup key.
The redesign's device cards will therefore need a new presentation layer on top of the
existing data model, not a change to the BlueZ layer.

## 4. BlueZ backend

- Package `blueman/bluez/`: `Base.py` (proxy base, `_properties_changed`), `Manager.py`
  (object manager, `assert isinstance(…, Gio.DBusProxy)`), `Adapter.py`, `Device.py`,
  `Agent*`, `obex/Transfer.py`, `obex/…`.
- `Base.py:49` creates a proxy with `Gio.DBusProxy.new_for_bus_sync` — **synchronous**
  at construction. Callers constructing proxies from the UI thread block the main loop.
  (See BUG_AUDIT.md, B-03.)
- `AnyBase.__init__` uses `Gio.bus_get_sync(SYSTEM)` during construction.
- `Base.get()` and `get_properties()` issue synchronous Properties.Get/GetAll calls;
  `__getitem__` delegates to `get()`. `ManagerDeviceList.row_setup_event` and
  `filter_func` reach these from GTK callbacks. Cached properties are a fallback
  after Get fails, not the default read path.
- `Base.set()` issues asynchronous Properties.Set without a completion callback;
  surrounding Python try/except cannot observe a remote rejection. See corrected B-06.
- `bluez/Manager.py` already owns a `Gio.DBusObjectManagerClient`. Evaluate its
  cached properties/signals for the new presentation, without replacing BlueZ APIs.

## 5. D-Bus services exported by Blueman

| Bus name / interface | Source | Purpose |
|---|---|---|
| `org.blueman.Applet` (`AppletService.NAME`) | `blueman/main/Applet.py` | Applet control, menu |
| `org.blueman.Applet.StatusIcon` | `blueman/plugins/applet/StatusIcon.py` | Tray icon state, used by Manager via `DBusProxies.py` |
| `org.blueman.Applet.PowerManager` | `blueman/main/DBusProxies.py` | Adapter power state |
| `org.blueman.Mechanism` (privileged helper, system bus) | `blueman/main/MechanismApplication.py:44`, `DBusProxies.py:57` | Privileged operations (network, rfcomm, rfkill plugins under `blueman/plugins/mechanism/`) |
| `org.blueman.Services` (application id) | `blueman/main/Services.py:21` | Service/profile window application |

Renaming any of these would break external scripts and the privilege-escalation
setup. The policy is `data/configs/org.blueman.policy.in`; rules are in
`data/configs/blueman.rules`, and bus configuration is
`data/configs/org.blueman.Mechanism.conf`. **Preserve identifiers** (plan §6).

## 6. Plugin architecture

- Base classes: `blueman/plugins/BasePlugin.py` (includes a `GSettings` TypedDict),
  `AppletPlugin.py`, `ManagerPlugin.py` (in `blueman/plugins/`), `ServicePlugin.py`,
  `MechanismPlugin`.
- Loader: `blueman/main/PluginManager.py`. Plugins are discovered by importing the
  package modules; dependency checks use `__depends__` / `__conflicts__`.
- Service plugins are discovered through `ServicePlugin.__subclasses__()`
  (`blueman/main/Services.py:82`).
- Lifecycle hooks confirmed in code: `on_load` / `on_unload` (`BasePlugin.py:82,86`).
  The manager emits `adapter-changed` on `ManagerDeviceList` (`Manager.py:163`,
  `ManagerStats.py:26`, `ManagerToolbar.py:25`). Compatibility rule for the redesign:
  keep these hooks and typed signals, plus `List.selected()`, `get()`, `compare()`,
  the backing model/filter and selection semantics. `ManagerDeviceMenu.generate()`
  uses pointer hit-testing and filter-to-child iter conversion. ManagerMenu and
  ManagerToolbar receive `Gtk.TreeIter` in device signals. Keeping row dictionaries
  alone is insufficient. Plugin `MenuItemsProvider` callbacks receive the menu,
  Device, and powered state; preserve their generated actions too.

## 7. System tray

- Two implementations selected at runtime by `StatusIcon.py`
  (`GetStatusIconImplementations`): `GtkStatusIcon` (deprecated `Gtk.StatusIcon`,
  `indicators/GtkStatusIcon.py:59`) and `StatusNotifierItem` (SNI over D-Bus,
  `indicators/StatusNotifierItem.py:136`).
- `Gtk.StatusIcon` is deprecated in GTK 3.14+ but still the fallback. Keep both.

## 8. Settings

- Single schema: `data/org.blueman.gschema.xml`, path and schema IDs `org.blueman.*`
  (e.g. `org.blueman.general` used at `Manager.py:72`).
- Window geometry already persisted: `window-properties` key read at `Manager.py:116`
  and written in `_on_configure`. **Reuse this key for the modern window size.**
- Manager toolbar/statusbar visibility uses the existing `show-toolbar` and
  `show-statusbar` keys (`Manager.py:95-96`). These must keep working until the
  toolbar is replaced.

## 9. Notifications

- `blueman/gui/Notification.py`: custom `_NotificationBubble(Gio.DBusProxy)` talking to
  `org.freedesktop.Notifications` directly over the session bus (`Notification.py:121,289`).
  No libnotify dependency. Good base for "avoid duplicate notifications" work.
- Notifications are not centralised: callers in applet and manager plugins call it
  directly. There is no dedupe layer.

## 10. Pairing and agent

- Agent: `blueman/main/applet/BluezAgent.py` (applet-side, registers with BlueZ).
- Passkey/PIN dialog: `data/ui/applet-passkey.ui`.
- Plugin `AuthAgent` (`blueman/plugins/applet/AuthAgent.py`) also exists; its interaction
  with `BluezAgent` is lifecycle ownership: it creates/registers the agent when
  BlueZ appears and unregisters on unload. BlueZ release invokes agent cancellation.
- `BluezAgent` supports PIN/passkey entry/display, confirmation, service authorization,
  and Cancel/Release. It uses both `applet-passkey.ui` and Notification objects;
  restyling the XML alone does not modernize all authorization prompts.
- Authorization/confirmation requests are presented by the applet; the manager
  performs bond/trust actions via `blueman/bluez/Device.py`.

## 11. File transfer

- Send: `blueman/main/Sendto.py`, `sendto/`, `data/ui/send-dialog.ui`,
  `sendto-device-dialog.ui`, `sendto-rowbox.ui`.
- Receive runtime/authorization: `blueman/plugins/applet/TransferService.py`
  (OBEX Agent, accepted-transfer bookkeeping, destination move, notifications).
- Receive preferences: `blueman/plugins/services/Transfer.py`,
  `data/ui/services-transfer.ui` (shared path and trusted-device acceptance).
- OBEX object: `blueman/bluez/obex/Transfer.py` (properties-changed based progress).

## 12. Audio

- `blueman/plugins/manager/PulseAudioProfile.py` (Pulse/PipeWire profile switching),
  `blueman/main/PulseAudioUtils.py`, `blueman/plugins/applet/*` for per-device audio menu.
- Tests exist for PulseAudio utils (`test/main/test_pulseaudio_utils.py`).

## 13. Build and packaging

- **Meson** is the primary build (`meson.build`, `meson_options.txt`, version `2.4.3`,
  meson >= 0.56, meson 1.3.2 on dev box). Autotools files (`configure.ac`,
  `Makefile.am`, `autogen.sh`) are still present and maintained in parallel.
- Resource installation: `data/ui/*.ui`, `data/icons/hicolor/scalable/**.svg`,
  `data/org.blueman.gschema.xml`. **No CSS resource and no theme resource are
  installed yet.** Adding `data/themes/*.css` requires meson `install_data` entries and
  a file-based loader decision (see plan). Autotools uses explicit Python/resource
  lists: update `Makefile.am` files and `configure.ac` for new subdirectories too.
  Meson uses `install_subdir` for Python and UI files; it must exclude new build files.
- `Constants.py` is generated at configure time: Meson writes it in the build root
  and installs it into the Python package; Autotools configures `blueman/Constants.py`. Running tests from a
  source checkout without a build fails (see BUG_AUDIT.md, T-01).

## 14. Tests

- Layout: `test/` mirrors `blueman/`. Most files are `test_imports.py` (import smoke
  tests). Real behaviour tests: `test/main/test_dbus_proxies.py`,
  `test_dns_server_provider.py`, `test_gdbus_error.py`, `test_netconf.py`,
  `test_pppconnection.py`, `test_pulseaudio_utils.py`, `test_speedcalc.py`,
  `test/plugins/mechanism/test_rfcomm.py`, `test/services/meta/test_network_service.py`,
  `test/bluez/obex/test_manager.py`, `test/bluez/test_manager.py`,
  `test/test_gobject.py`.
- `test/testhelpers/DBusMock.py` exists but depends on the external `dbusmock` package,
  which is not installed on the dev box.
- Current attempt (2026-10-15, Python 3.12.3, unconfigured checkout):
  `python3 -m unittest` ran **258 tests; 37 failures, 83 errors**. Missing generated
  `blueman.Constants` and missing `dbusmock` dominate the output. Log:
  `/tmp/blueman-phase0-unittest.log` (temporary local evidence).
- Configured baseline: **BLOCKED**. `./autogen.sh` stops because `autoreconf` is
  missing. `autopoint`, `cython3`, `xvfb-run` are also absent; pkg-config cannot
  find `pygobject-3.0` or `bluez`. No dependencies were installed in this audit.
- `.github/workflows/check.yml` specifies configure → `make -C module` →
  `PYTHONPATH=module/.libs python3 -m unittest`, with python-dbusmock and system
  development/runtime packages. Its `/dev/rfkill` fixture is for its isolated
  container; do not reproduce that step against a real host device node.
- Meson has no registered tests in this checkout. `meson test` cannot establish
  the unit-test baseline. Earlier pytest counts were not rerun and are not a
  supported current baseline; import suites use unittest `load_tests` hooks.

## 15. Upstream comparison

On 2026-10-15, `git ls-remote --symref https://github.com/blueman-project/blueman.git HEAD`
resolved the default branch to `main`. Fetching `main` into FETCH_HEAD returned
`67cea9010c114f1fd9df966d52a53b0a7f68f47f`, exactly the local HEAD.
`git rev-list --left-right --count HEAD...FETCH_HEAD` returned `0 0`;
`git diff --stat HEAD FETCH_HEAD` was empty. No upstream changes were merged and
no remote configuration was changed. This comparison covers committed source;
the five untracked project Markdown files are local additions.

Issue sampling is recorded in BUG_AUDIT.md. Reports on older releases are test
scenarios, not proof of a current local defect. There are no newer commits in the
fetched upstream main snapshot to cherry-pick.

## 16. Lifecycle and redesign constraints

- `Manager.on_dbus_name_vanished` hides the window, runs an ErrorDialog, then quits.
  Its FIXME is misleading: automatic recovery is not implemented. Keep this
  existing limitation visible in acceptance results until Phase 9.
- `DeviceList.destroy` disconnects its device/adapter/manager/selection handlers.
  Discovery uses a GLib timeout with no retained source ID; `stop_discovery` clears
  the flag. The new presentation must own and clean up all sources it adds.
- `ManagerDeviceList` polls connected-device levels every second. Invalid row
  references or disconnection stop each monitor. Battery values come from Battery1;
  RSSI/TPL fallback bars can be synthetic (B-10). New cards must not present these
  fallback values as measured telemetry.
- `Tray.py` loads the indicator implementation list at runtime and exits when the
  applet name disappears. Keep both SNI and Gtk.StatusIcon implementations.
- `DiscvManager` manages adapter *discoverability*, distinct from device discovery.
  Its timeout lifecycle is recorded in B-12.
- Manager actions already expose inquiry, bond, trust, remove, send, plugins,
  services and adapter preferences. Connection/profile actions route through
  ManagerDeviceMenu and applet service plugins; preserve those routes.

## 17. Verification limits

Static reading covered Manager, ManagerDeviceList, ManagerDeviceMenu, DeviceList,
Adapter, Device, AnyBase, PluginManager, DiscvManager, AuthAgent/BluezAgent,
Sendto and its OBEX signal declarations, Tray, and receive runtime/preferences.
This is not an exhaustive correctness proof. Desktop-specific tray rendering,
third-party plugins, pairing races, transfers, audio/network/serial devices,
shutdown ordering and BlueZ restart recovery require configured runtime tests.
No hardware operations, deployments, bug fixes, or production UI changes were made.
