# TODO

Project-wide rescan findings per AGENTS.md categories. Format: `id | status | effort | description | notes`.

Status: `open`, `in-progress`, `blocked`. Effort: `S` (≤1h), `M` (half-day), `L` (≥1 day).

---

## security

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|

## input validation / command safety

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cmd-1 | open | S | `sendto/blueman_sendto.py.in:20-28` builds a shell-style command line by wrapping file paths in double quotes and passing the joined string to `Gio.AppInfo.create_from_commandline`. A filename containing quotes or command separators can break argument boundaries when launched through the desktop shell parser. | Build a `Gio.AppInfo`/`Gio.Subprocess` invocation from an argv vector, or escape with GLib shell-quoting for every path. Add a regression test with spaces, quotes, and semicolons in filenames. Cross-ref test-1. |

## data integrity

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| data-2 | open | S | `blueman/plugins/manager/Notes.py:32-35` creates a `.vnt` temporary file with `delete=False` and relies on the launched sendto process to delete it. If launch fails or the process never starts, the note body remains in `/tmp` indefinitely. | Delete the temp file when `launch()` returns false or raises; consider creating it in an app-owned temp directory with cleanup on startup. Cross-ref gov-5. |

## performance

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| perf-5 | open | M | `blueman/bluez/Manager.py:115-149` `get_adapter_paths`/`get_devices` iterate `_object_manager.get_objects()` per call | cache, invalidate on object-added/removed |
| perf-10 | open | S | `blueman/gui/manager/ManagerMenu.py:53` creates Adapter proxies for all adapters in `__init__` | lazy-instantiate on selection |
| perf-13 | open | S | `blueman/main/Applet.py:93-118` plugin broadcast loop runs full plugin set per property change → O(plugins × props × devices) | debounce/batch property events |
| perf-9 | open | S | `blueman/main/DhcpClient.py:48-50,68` `subprocess.poll()` blocking in 1s `GLib.timeout` | use `Gio.Subprocess` + `wait_check_async` or `GLib.child_watch_add` |
| perf-11 | open | S | `blueman/main/Manager.py:161-164` `find_device()` linear scan over all objects | address-indexed dict |
| perf-1 | open | M | `blueman/main/ManagerStats.py:107` polls device stats via `GLib.timeout_add(1000, ...)` every second | switch to event-driven update or `timeout_add_seconds` |

## scalability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| scale-3 | open | S | `blueman/main/BatteryWatcher.py:18` creates `Battery` per creation signal without dedup | check existence before create |
| scale-1 | open | M | `blueman/main/Manager.py:149-159` `populate_devices` emits per-device add signal serially | single batch signal |
| scale-2 | open | S | `blueman/main/PulseAudioUtils.py:216-218` PA subscribe callback fires unthrottled on rapid card changes | debounce |

## caching strategy

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|

## concurrency

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| conc-3 | open | S | `blueman/main/PulseAudioUtils.py:372-379` `weakref.proxy(self)` in callback silently no-ops if GC'd | hold hard ref or explicit lifecycle |

## code complexity

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cx-3 | open | L | `blueman/gui/manager/ManagerDeviceList.py:412-540` 4 coupled power-level methods (>100 LOC) | extract `PowerLevelMonitor` class |
| cx-1 | open | M | `blueman/gui/manager/ManagerDeviceList.py:453` `row_update_event` 7-elif on property name | dict dispatch `{key: handler}` |
| cx-5 | open | M | `blueman/gui/manager/ManagerDeviceList.py:553` `tooltip_query` ~102 LOC nested conditions | extract `TooltipBuilder` |
| cx-2 | open | M | `blueman/main/Manager.py:224` `simple_action()` 13-case match mixes routing + business logic | extract `{action: (handler, needs_device)}` table |
| cx-4 | open | M | `blueman/main/PluginManager.py:132-174` `__load_plugin` ~43 LOC, 15+ conditionals (deps/conflicts/priority) | extract `PluginDependencyResolver` |
| cx-6 | open | S | `blueman/main/Services.py:58` `on_query_apply_state` returns -1/bool mixed protocol | replace with `ApplyState` enum |

## code duplication

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dup-4 | open | S | `blueman/gui/manager/ManagerDeviceList.py:498-540` `_update_power_levels` + `_disable_power_levels` duplicate bar lookup | extract `BarRenderer` |
| dup-5 | open | S | `blueman/gui/manager/ManagerDeviceList.py:655-677` `_set_cell_data` repeats if/elif for battery/rssi/tpl | polymorphic bar renderers |
| dup-2 | open | S | `blueman/gui/manager/ManagerDeviceMenu.py:141-188` `connect_service`/`disconnect_service` duplicate nested success/error callbacks | extract async-DBus template |
| dup-6 | open | S | `blueman/main/Applet.py:78-90` `_on_dbus_name_appeared/_vanished` repeat plugin notify loop | `_notify_manager_state_change(state)` |
| dup-1 | open | M | `blueman/main/Applet.py:92-118` 8× identical plugin broadcast loops | `_broadcast(event, *args)` helper |
| dup-8 | open | S | `blueman/main/Services.py:86` bare `except:` with `# noqa: E722` | narrow to expected exceptions |

## API contract & compatibility

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| api-1 | open | S | `blueman/main/DBusProxies.py:91` exposes the Python proxy method as `dchp_client`, while the DBus method and interface are `DhcpClient`. The typo is now part of the local Python call surface and makes future refactors/API docs error-prone. | Add correctly spelled `dhcp_client()` as the public method, keep `dchp_client()` as a deprecated alias until callers/tests migrate, then remove the alias in a later cleanup. |

## architecture/modularity/SOLID

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| arch-8 | open | S | `blueman/gui/manager/ManagerDeviceList.py:334-351` UI-formatting `@staticmethod`s placed on liststore class | move to `DeviceDisplayFormatter` |
| arch-7 | open | S | `blueman/gui/manager/ManagerDeviceMenu.py:64-65` `__ops__`/`__instances__` class-level globals | DI or event-emitter |
| arch-1 | open | L | `blueman/main/Applet.py:25-148` `BluemanApplet` is God object (init Manager, plugins, broadcasts, state) | extract `PluginBroadcaster`, `ManagerWatcher` |
| arch-2 | open | L | `blueman/main/Manager.py:37-363` `Blueman` mixes lifecycle, UI, device actions, settings | split into `ManagerUI`, `DeviceActionHandler`, `SettingsManager` |
| arch-5 | open | S | `blueman/main/MechanismApplication.py:15-39` Timer reads `BLUEMAN_SOURCE` env var for test mode | subclass `TestTimer` or inject duration |
| arch-4 | open | M | `blueman/main/MechanismApplication.py:42-100` mixes timer, PolicyKit, plugin loading, DBus registration | extract `TimerManager`, `PluginLoader` |
| arch-6 | open | S | `blueman/main/PluginManager.py:139,200` raise bare `Exception(...)` | introduce `PluginDependencyError`, `PluginError` |
| arch-3 | open | M | `blueman/main/PluginManager.py:176` `__getattr__` magic for plugin lookup breaks IDE/refactor | explicit `get_plugin(name)` accessor |

## decoupling

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dec-3 | open | S | `blueman/plugins/applet/AutoConnect.py:62` `self.parent.Manager.find_device()` reach-through | `parent.find_device_by_address(addr)` API |
| dec-4 | open | S | `blueman/plugins/applet/KillSwitch.py:147-149` direct `self.parent.Plugins.StatusIcon/PowerManager` access | optional plugin query w/ fallback |
| dec-6 | open | S | `blueman/plugins/AppletPlugin.py:32` hardcoded fallback icon name | constant + GSettings override |
| dec-5 | open | S | `blueman/plugins/manager/Services.py:82` plugin discovery via `ServicePlugin.__subclasses__()` | registry or `importlib.metadata.entry_points` |
| dec-2 | open | M | `blueman/plugins/manager/Services.py:8` `ManagerPlugin` imports `ManagerDeviceMenu`, `MenuItemsProvider` (GUI layer) | event-based provider interface |

## business/design patterns/DDD

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| pat-2 | open | S | `on_query_apply_state` magic-return protocol | State enum (DDD value object) |
| pat-1 | open | M | `row_update_event`, `simple_action`, `_set_cell_data` all have type/key switch ladders | Strategy or dispatch-table |
| pat-3 | open | M | Plugin lifecycle scattered (load/unload/deps/conflicts/state) | introduce `PluginLifecycle` state machine |

## reliability/correctness

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| rel-11 | open | S | `blueman/main/applet/BluezAgent.py:201-203` indexes `key[entered]` when displaying a passkey. If BlueZ reports `entered == 6` after all digits are typed, or an invalid value, the notification path raises `IndexError`. | Clamp `entered` to the valid range and render the fully-entered passkey without bolding a missing digit. Cross-ref test-2. |
| rel-9 | open | S | `blueman/main/Services.py:86` bare `except: pass` hides errors | narrow exception types |
| rel-12 | open | S | `blueman/plugins/BasePlugin.py:50` registers `weakref.finalize(self, self._on_plugin_delete)`. Passing a bound method keeps `self` strongly referenced by the finalizer, so plugin instances may not be collected and the delete hook is unreliable. | Register a module-level/static cleanup callback with weak state, or rely on explicit plugin unload and remove the finalizer. |

## observability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| obs-4 | open | S | `blueman/bluez/obex/Manager.py:51,59,68,75` `logging.info(object_path)` lacks event/context | prefix with event name |
| obs-10 | open | S | `blueman/gui/GenericList.py:116` silent `ValueError` from `get_iter` | `logging.debug` invalid path |
| obs-9 | open | S | `blueman/gui/GtkAnimation.py:79` silent `ZeroDivisionError` on duration=0 | `logging.debug("Animation duration zero")` |
| obs-7 | open | S | `blueman/gui/Notification.py:169` silent `ValueError` on notification hints | `logging.debug` unsupported hint |
| obs-11 | open | S | `blueman/main/DNSServerProvider.py:48` `GLib.Error` swallowed | `logging.debug("DNS lookup failed, using fallback")` |
| obs-3 | open | S | `blueman/main/Manager.py:62` `print()` in exception handler | `logging.error(..., exc_info=True)` |
| obs-6 | open | S | `blueman/main/PluginManager.py:64,123` `LoadException` swallowed silently | `logging.warning` with plugin name |
| obs-15 | open | S | `blueman/plugins/applet/AutoConnect.py:116-117` ignores automatic connection failures with `pass`, so failed auto-connect attempts leave no log trail and are hard to diagnose. | Log the target service/device and failure reason at debug or warning level, with rate limiting if needed. |
| obs-12 | open | S | `blueman/plugins/mechanism/Network.py:46` exception only routed to error callback, no local log | add `logging.error` with trace |
| obs-14 | open | S | `sendto/blueman_sendto.py.in:14,17,29,33` `print()` for user-facing messages | replace with `logging` where plugin host allows |

## wiring gaps

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|

_(none open)_

## unused functions/methods

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|

_(none open)_

## STRIDE

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| stride-1 | open | M | `blueman/main/DbusService.py:162-170` unhandled exceptions return full traceback in DBus errors, leaking internal paths to any caller | sanitize error messages on the bus; detailed traces to daemon log only |
| stride-4 | open | M | `blueman/main/MechanismApplication.py:50` if `POLKIT=False` at build, PolicyKit auth skipped silently (Elevation of privilege) | fail-closed; never silently skip authorization; log when disabled |

## data governance

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| gov-3 | open | M | `blueman/plugins/applet/NetUsage.py:40,64-65` per-device tx/rx stats persisted at `/org/blueman/plugins/netusages/{Address}/` reveal connection history + volume | document retention; add auto-expire option |
| gov-4 | open | S | `blueman/plugins/applet/RecentConns.py:120` user device aliases (may contain PII) stored plaintext | document plaintext storage; UI warning |
| gov-1 | open | M | `blueman/plugins/applet/RecentConns.py:127-139` device object paths + UUIDs stored unencrypted in GSettings | store only address/UUID; audit schema permissions |
| gov-2 | open | S | `blueman/plugins/applet/RecentConns.py:144` BT addresses (quasi-permanent IDs) logged via `logging.info` | redact/rate-limit address logging in production |
| gov-5 | open | S | `blueman/plugins/manager/Notes.py:32-35` can leave plaintext note bodies in temporary `.vnt` files when send launch fails. These notes are user-authored content and can include sensitive data. | Ensure temp-note lifecycle is owned by Blueman until a child process has definitely taken responsibility; clean stale `note*.vnt` files where safe. Cross-ref data-2. |

## multithreading

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| mt-1 | open | S | `blueman/gui/manager/ManagerMenu.py:96` `GLib.idle_add()` return value/source id ignored; no cleanup if parent destroyed | store source id, remove on teardown |

## watchdog

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| wd-3 | open | M | `blueman/main/DhcpClient.py:49-50` two `timeout_add` sources, neither stored; `_check_client` keeps polling dead process after `_on_timeout` | store + `source_remove` both on exit (overlaps rob-3) |
| wd-8 | open | S | `blueman/main/indicators/StatusNotifierItem.py:32-42` starts a repeating revision-advertisement timeout and discards the source id. The menu service cannot remove the source on unregister/teardown, so it can keep emitting after the tray path is gone. | Store the source id and remove it in an explicit `unregister`/delete path; add a test that teardown removes the source. |
| wd-2 | open | M | `blueman/main/PPPConnection.py:76` `cleanup()` only closes fd, leaves io_watch/timeout sources registered | remove all GLib sources in cleanup (overlaps rel-7) |
| wd-1 | open | M | `blueman/main/PPPConnection.py:82-87` pppd spawned with no liveness monitoring; orphan pppd possible on error path | add `GLib.child_watch_add`, kill on cleanup |
| wd-6 | open | S | `blueman/plugins/applet/PPPSupport.py:40` synchronous `Popen(['ps'])` blocks main loop until ps returns | use async `Gio.Subprocess` |
| wd-4 | open | M | `blueman/plugins/mechanism/Rfcomm.py:14` rfcomm watcher Popen fire-and-forget, no PID tracking/liveness; only killed via grepped `ps` | track PID, supervise (overlaps sec-2, rel-8) |
| wd-5 | open | M | `blueman/services/meta/SerialService.py:75` `Popen([RFCOMM_WATCHER_PATH])` no exit/return-code monitoring; crash leaves rfcomm broken | child watch + restart/notify |

## state machine

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| sm-4 | open | M | `blueman/main/DhcpClient.py:39-51` no state flag; `_check_client` + `_on_timeout` both call `querying.remove()` → possible `ValueError` | guard with done-flag, single removal (overlaps wd-3, rob-3) |
| sm-5 | open | M | `blueman/main/NetworkManager.py:38,69-70` `_statehandler` asserted not-None but state change can fire before assignment | assign handler before connect / null-guard |
| sm-2 | open | M | `blueman/main/PPPConnection.py:181-210` `on_data_ready` can run cleanup while `on_timeout` still pending → double `error-occurred` emit | explicit connection-state guard, single emit |
| sm-3 | open | L | `blueman/main/PPPConnection.py:213-224` `on_timeout` closure captures stale `command_id` if `send_commands` reused before fire | bind per-command state / cancel prior timeout |
| sm-6 | open | L | `blueman/plugins/applet/PowerManager.py:97,109` Callback timer source id not tracked; orphan timeout fires on GC'd object | store source id, remove in destructor |
| sm-9 | open | S | `blueman/plugins/applet/ShowConnected.py:86-92` schedules delayed `enumerate_connections()` calls on every manager-state-enabled event without storing/canceling the source. A fast state flap can let a stale enumeration update the icon after the manager is disabled. | Store the pending source id, cancel it on manager disable/unload, and ignore callbacks if manager state changed. |

## composition

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| comp-2 | open | M | `blueman/bluez/obex/Base.py:5` obex Base subclasses bluez Base, both override metaclass attrs; class-attr duplication | pass bus config to `__init__` instead of subclassing |
| comp-3 | open | S | `blueman/gui/manager/ManagerDeviceList.py:45` 4-level inheritance (Gtk.TreeView→GenericList→DeviceList→ManagerDeviceList) + parent-chain coupling | inject deps via constructor, prefer composition |
| comp-4 | open | M | `blueman/plugins/MechanismPlugin.py:8-12` copies parent methods (timer, confirm_authorization) into `__init__`; tight bind to concrete app | abstract plugin interface + DI |

## dependency

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dep-5 | open | S | `blueman/main/Applet.py:10` wildcard `from blueman.Functions import *` obscures deps | explicit imports |
| dep-7 | open | M | `blueman/main/DNSServerProvider.py:12` hardcoded `RESOLVER_PATH="/etc/resolv.conf"` | configurable + DNSProvider abstraction (dup cfg-004) |
| dep-2 | open | L | `blueman/main/NetworkManager.py:9-12` import-time `gi.require_version` raises if NM bindings missing | move into lazy init try-block |
| dep-1 | open | L | `blueman/main/PulseAudioUtils.py:14-18` import-time `CDLL` load raises ImportError if libpulse absent, failing module | lazy loader + optional-support flag |
| dep-4 | open | L | `blueman/plugins/applet/GameControllerWakelock.py:14-16,22-23` import-time GdkX11/X11 screen check raises | move platform check to `on_load()` |
| dep-6 | open | S | `blueman/plugins/applet/NetUsage.py:8` wildcard import from `blueman.Functions` | explicit imports |
| dep-3 | open | L | `blueman/plugins/mechanism/RfKill.py:6-7` import-time `/dev/rfkill` check raises, blocks plugin discovery on systems without it | move check to `on_load()` |

## adaptability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| adapt-1 | open | M | `blueman/gui/manager/ManagerDeviceMenu.py:225-242` hardcoded BlueZ error-string mapping with version-specific comments; breaks on newer BlueZ | parse error codes dynamically + version detect |
| adapt-4 | open | S | `blueman/main/DbusService.py` bus type hardcoded to SESSION; assumes single-user desktop | make bus_type configurable |
| adapt-2 | open | M | `blueman/main/Functions.py:104` (`blueman/Functions.py:104`) `time.clock_gettime(CLOCK_MONOTONIC_RAW)` fallback not portable | use `GLib.get_monotonic_time()` consistently |
| adapt-3 | open | M | `blueman/plugins/mechanism/Ppp.py:24` hardcoded `/dev/rfcomm{port}` template | inject device-path factory |

## extensibility

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| ext-7 | open | S | `blueman/gui/DeviceList.py:147-162` override hooks only; no registry for third-party extensions | signal-based hooks / extension protocol |
| ext-5 | open | M | `blueman/main/indicators/IndicatorInterface.py` StatusIcon vs StatusNotifierItem hardcoded; no pluggable indicator backend | IndicatorBackend protocol via PluginManager |
| ext-1 | open | M | `blueman/main/PluginManager.py:132-174` load logic embedded in manager; hard to add plugin types/async loaders | extract LoadStrategy / load pipeline |
| ext-6 | open | M | `blueman/plugins/applet/Menu.py` menu structure hardcoded; plugins can't extend menus without parent coupling | MenuRegistry / signal-based insertion |
| ext-2 | open | M | `blueman/plugins/AppletPlugin.py:35-41` DBus service opt-in via `__dbus_iface_name__` is intricate | `@dbus_service` decorator / ServiceRegistry |
| ext-3 | open | L | `blueman/plugins/ServicePlugin.py:12-62` separate hierarchy from BasePlugin; no depends/conflicts declarations | unify to BasePlugin, add `__depends__`/`__conflicts__` |
| ext-4 | open | M | `blueman/services/meta/NetworkService.py` new service types must implement props; no extension hooks | ServiceRegistry + `@service_provider` |

## legacy

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| leg-7 | open | S | `blueman/bluez/Device.py:22,29` `# type: ignore` on connect/disconnect masking signature mismatch | resolve override signatures |
| leg-8 | open | S | `blueman/bluez/Network.py:17,26` `# type: ignore` on connect/disconnect | resolve signatures |
| leg-6 | open | S | `blueman/gui/GtkAnimation.py:200` FIXME `Gtk.render_background()` wrong colors | investigate + fix or document |
| leg-4 | open | M | `blueman/gui/manager/ManagerMenu.py:45,47` `Gtk.ImageMenuItem` in manager UI | migrate to `Gtk.MenuItem` |
| leg-9 | open | S | `blueman/main/indicators/GtkStatusIcon.py:44` `# type: ignore` on submenu enumerate | proper overload/typing |

## configuration

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cfg-7 | open | S | `blueman/config/AutoConnectConfig.py:10` GSettings schema id hardcoded, duplicated across plugins | module constant |
| cfg-1 | open | M | `blueman/Constants.py.in:22` `BLUEMAN_SOURCE` env var checked inline, undocumented feature flag | centralize in config module + document |
| cfg-5 | open | S | `blueman/main/DhcpClient.py:17-20` DHCP client search order hardcoded (dhclient/dhcpcd/udhcpc) | configurable list |
| cfg-4 | open | M | `blueman/main/DNSServerProvider.py:12` hardcoded `/etc/resolv.conf`, precedence undocumented | document resolved-first precedence |
| cfg-2 | open | M | `blueman/main/MechanismApplication.py:25` idle timeout hardcoded (30s / 9999 dev) keyed on `BLUEMAN_SOURCE` | make configurable, document dev mode (overlaps arch-5) |
| cfg-6 | open | M | `blueman/plugins/services/Network.py` DHCP handler selection (dnsmasq/dhcpd/udhcpd) no user config, undocumented fallback chain | document + expose config |

## platform

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| plat-2 | open | M | `blueman/main/PPPConnection.py:83` hardcoded `/usr/sbin/pppd` | dynamic `have()` lookup |
| plat-5 | open | M | `blueman/plugins/applet/KillSwitch.py:59,87` hardcoded `/dev/rfkill`, silent fail without it | feature-detect + graceful degrade |
| plat-7 | open | M | `blueman/plugins/applet/NetUsage.py:84,87` hardcoded `/sys/class/net` sysfs paths, Linux-only | abstraction + degrade |
| plat-6 | open | S | `blueman/plugins/mechanism/RfKill.py:6` module-level `/dev/rfkill` check raises at import (dup dep-3) | move to `on_load()` |
| plat-10 | open | S | `blueman/services/meta/SerialService.py` hardcoded `/dev/rfcomm{port}` naming | abstract device node |

## data structure

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| ds-5 | open | M | `blueman/bluez/Manager.py:160-164` `find_device()` scans all DBus objects, repeated Address lookups | cached device index (dup perf-11, scale) |
| ds-2 | open | M | `blueman/plugins/applet/NetUsage.py:261-268` linear liststore scan by address in `monitor_added` | address→iter dict |
| ds-3 | open | M | `blueman/plugins/applet/NetUsage.py:276-283` linear liststore scan by address in `monitor_removed` | address→iter dict |
| ds-4 | open | M | `blueman/plugins/applet/RecentConns.py:129-137` linear scan of `stored_items` by (adapter,address,uuid) | tuple-keyed dict |

## vectorization

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| vec-2 | open | L | `blueman/bluez/Manager.py:138-149` `get_devices()` rescans all objects per `find_device()` | cache indexed by adapter, batch GetAll (dup perf-5) |

## robustiness

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| rob-8 | open | S | `blueman/gui/Animation.py:28-35` `start()` is not idempotent: calling it twice overwrites `self.timer` and leaks the first `GLib.timeout_add` source, so `stop()` can remove only the newest timer. | Return early if already started, or stop the existing source before starting a new one; add a start/stop source-id test. Cross-ref test-4. |
| rob-2 | open | M | `blueman/gui/manager/ManagerProgressbar.py:117` `timeout_add(timeout,finalize)` id discarded; double-finalize | capture + remove before re-call |
| rob-1 | open | M | `blueman/gui/manager/ManagerProgressbar.py:178` `timeout_add(41,pulse)` source id not captured; pulses after `stop()` | store + remove source id (overlaps perf-14) |
| rob-3 | open | M | `blueman/main/DhcpClient.py:49-50` two timeout sources never stored/removed (dup wd-3) | store ids, remove on exit |
| rob-5 | open | S | `blueman/main/PPPConnection.py:182-197` OSError path may skip `source_remove(io_watch)` before cleanup → leaked source | remove source in except (overlaps rel-7) |
| rob-6 | open | S | `blueman/plugins/applet/NetUsage.py:79-80` Monitor `__del__` doesn't remove timeout source | guard + `source_remove(poller)` |

## ui / ux

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| ux-7 | open | S | `blueman/gui/manager/ManagerDeviceList.py:508` FIXME "horrible workaround" inadequate feedback | proper user feedback |
| ux-3 | open | S | `blueman/gui/manager/ManagerProgressbar.py:50` hardcoded progressbar 100x15 | flexible sizing |
| ux-5 | open | S | `blueman/gui/Notification.py:107-108` empty `add_action()` stub logs warning | implement or remove stub |
| ux-4 | open | M | `blueman/gui/Notification.py:168-169` bare `except ValueError: pass` on hint set (dup obs-7) | log when fallback occurs |
| ux-2 | open | S | `blueman/gui/Notification.py:51` hardcoded notification size 350x50 | responsive sizing |
| ux-8 | open | S | `blueman/main/Manager.py:183` FIXME BlueZ stop/start not surfaced to user | notification/infobar on daemon loss |

## accessibility

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| a11y-1 | open | S | `blueman/gui/applet/PluginDialog.py:87-112` dynamically creates labels next to `Gtk.SpinButton`/`Gtk.Entry` controls but does not set mnemonic widgets or accessible label relationships. Screen readers and keyboard users get weaker context for plugin preference fields. | Use mnemonic labels (`use_underline`) where possible and set label/accessibility relationships for generated controls; add an accessibility smoke test for generated preference widgets. |

## i18n

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| i18n-2 | open | S | `blueman/main/applet/BluezAgent.py:201-229` builds authentication notification sentences by concatenating translated fragments with device names, PINs, and markup. Translators cannot reorder the whole sentence or place punctuation naturally. | Use one format string per complete sentence/message with named placeholders, e.g. `%(device)s` and `%(passkey)s`, preserving markup escaping. |
| i18n-1 | open | S | `sendto/blueman_sendto.py.in:46-50` hardcodes Nautilus/Caja/Nemo menu labels and tips in English, and `sendto/blueman_sendto.py.in` is not listed in `po/POTFILES.in`, so translators never see them. | Wrap file-manager extension labels/tips in gettext and add the generated/template source to extraction. |

## documentation

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| doc-7 | open | M | `blueman/gui/CommonUi.py` `ErrorDialog` lacks docstring; `excp` param undocumented | document exception UI |
| doc-3 | open | M | `blueman/gui/DeviceList.py` class docstring missing; signals only in `__gsignals__` | document model + key signals |
| doc-6 | open | M | `blueman/gui/DeviceSelectorDialog.py` `DeviceRow`/`DeviceSelector` lack docstrings | document selector pattern |
| doc-2 | open | M | `blueman/gui/GenericList.py` no module/class docstring | document TreeView wrapper + signals |
| doc-9 | open | M | `blueman/gui/GsmSettings.py` class lacks docstring | document GSM settings binding |
| doc-8 | open | S | `blueman/gui/manager/ManagerProgressbar.py` class undocumented (cancellable/text params) | document progress lifecycle |
| doc-5 | open | M | `blueman/gui/Notification.py` `Notification()` factory + bubble/dialog undocumented | document return-type selection |
| doc-4 | open | S | `blueman/main/Builder.py` class lacks docstring | document Gtk.Builder wrapper behavior |
| doc-10 | open | M | `README` lacks plugin/dev API docs | document plugin loading + extension points |

## test coverage

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| test-4 | open | S | No tests cover `blueman/gui/Animation.py` timer source lifecycle. The `start()`/`stop()` path can leak sources if `start()` is called repeatedly, and current tests would not detect it. | Add a focused test with mocked `GLib.timeout_add`/`source_remove` for idempotent start and complete cleanup. Cross-ref rob-8. |
| test-2 | open | S | No tests cover `BluezAgent._on_display_passkey` boundary values for `entered`. `blueman/main/applet/BluezAgent.py:201-203` indexes `key[entered]`, so an out-of-range or fully-entered value can crash the agent notification path. | Add focused tests for `entered` values 0, 5, 6, and invalid values; clamp or render without bolding when all digits are entered. |
| test-1 | open | S | No tests cover `sendto/blueman_sendto.py.in` command construction for selected file paths. The quoting bug in cmd-1 would pass unnoticed for paths with quotes, semicolons, or leading dashes. | Add a small unit test around the file-list-to-launch-command path after extracting it into a pure helper. Cross-ref cmd-1. |

## release & deploy engineering

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| releng-1 | open | S | `make_release.sh:3-7` archives `HEAD` using the latest tag name from `git describe --tags --abbrev=0`, without verifying that `HEAD` is exactly that tag or that the working tree is clean. A release tarball can be mislabeled with the previous tag or include unintended worktree attributes. | Require `git describe --tags --exact-match`, fail on dirty status, and print the commit/tag being archived. |
| releng-2 | open | S | `make_release.sh:9-16` produces `.tar.xz` and `.tar.gz` but no checksums or signatures. Downstream packagers/users have no release-integrity artifact from the script. | Generate SHA256 sums and optionally detached signatures as part of the release script, documenting the expected verification flow. |

## dependability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| depend-3 | open | S | `blueman/main/DNSServerProvider.py:29,102` `_get_servers_from_systemd_resolved`/`_subscribe_systemd_resolved` call `Gio.bus_get_sync(SYSTEM)` and `DBusProxy.new_for_bus_sync` with no error handling around bus/proxy acquisition (only the later `Get` at :48 is guarded). A briefly-unavailable system bus makes `__init__` raise and the whole provider fail rather than falling back to resolv.conf. | Wrap bus/proxy acquisition in try/except `GLib.Error` and degrade to the resolv.conf path. Cross-ref mem-2. |

## distributed systems

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dist-3 | open | S | `blueman/plugins/mechanism/Rfcomm.py:13-14` `_open_rfcomm` spawns a watcher per call with no dedup; two `OpenRFCOMM` calls for the same `port_id` start two `blueman-rfcomm-watcher /dev/rfcommN` processes, and `_close_rfcomm` kills only by matching the `ps` cmdline (can leave orphans or signal a recycled/foreign PID). | Before launching, scan for an existing watcher on that port and skip if present; track watcher PIDs in the mechanism rather than re-deriving from `ps`. Cross-ref wd-4, mem-1. |

## time & scheduling correctness

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| time-4 | open | M | `blueman/main/MechanismApplication.py:20-29` the idle-exit timer counts 1s `timeout_add` ticks (`self.time += 1` to 30) instead of comparing a monotonic deadline; GLib coalesces/delays timeouts under load or suspend, so the "30s idle" auto-exit drifts and can fire much later than intended. | Record `GLib.get_monotonic_time()` on activity and exit once `now - last >= 30s`, independent of tick count. Cross-ref cfg-2. |
| time-1 | open | M | `blueman/main/SpeedCalc.py:21` `calc()` keys elapsed-time/speed math on wall clock `time.time()`; an NTP step or manual clock change can skew the divisor across retained samples and produce erratic speeds (the zero-elapsed guard only catches exact ties/backsteps within the window). | Sample with `time.monotonic()` / `GLib.get_monotonic_time()`; a monotonic clock never steps. Distinct from ds-1 (log prune) and adapt-2 (clock_gettime portability). |
| time-3 | open | S | `blueman/plugins/applet/NetUsage.py:201` session duration `datetime.now() - fromtimestamp(config["time"])` is pure wall-clock; if the clock moved backward since the stored start, the delta is negative and renders nonsense durations. | Clamp negative deltas to 0 (or store a monotonic anchor) before formatting. |

## memory and cpu management

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| mem-2 | open | S | `blueman/main/DNSServerProvider.py:29-79` `_get_servers_from_systemd_resolved` issues a chain of synchronous `call_sync` D-Bus calls (Get DNS, then per-interface GetLink + DefaultRoute Get) with `-1` (infinite) timeout on the main loop whenever DHCP servers are resolved, scaling with interface count and able to hang indefinitely. | Use finite timeouts and/or move resolution off the main loop; cache across the `changed` signal instead of re-walking all links each call. Cross-ref depend-3. |
| mem-1 | open | S | `blueman/plugins/mechanism/Rfcomm.py:17` `_close_rfcomm` shells out `ps -e o pid,args` and `communicate()` synchronously inside the privileged mechanism D-Bus method, blocking the mechanism main loop while it scans every process to find one watcher PID. | Track watcher PIDs (from `Popen` in `_open_rfcomm`) keyed by port and kill by stored PID instead of scanning `ps`. Cross-ref dist-3. |

## system design

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| sysd-2 | open | M | `blueman/main/PluginManager.py:92,117` plugin discovery uses `plugin_class.__subclasses__()` (import side effects) and mutates shared class attributes (`cls.__unloadable__ = False`); two PluginManager instances (applet vs mechanism) or a reload mutate shared class state, so load order/conflict resolution is global, not per-manager. | Register plugins explicitly into a per-manager registry and keep per-instance load flags off the class object. Cross-ref dec-5, ext-1. |

## CLI / option integrity

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cli-3 | open | S | `apps/blueman-adapters.in:24` `--socket-id` (XEmbed) is undocumented — no `help=`, absent from `data/man/blueman-adapters.1` — yet plumbed into `BluemanAdapters(... socket_id)`. | Add `help=` text and document, or mark intentionally internal. |
| cli-2 | open | S | `apps/blueman-mechanism.in:38,57-58` `-d/--debug` only logs "Enabled verbose output" and does nothing else; the level is driven by `--loglevel`, so `--debug` does NOT enable debug logging — a dead/misleading flag. | Make `--debug` set `log_level = logging.DEBUG`, or remove it and document `--loglevel debug`. |
| cli-6 | open | S | `data/man/blueman-adapters.1:1` `.TH` header is `BLUEMAN-SENDTO` (copy-paste), so `man blueman-adapters` shows the wrong title/section. | Fix `.TH` to `BLUEMAN-ADAPTERS`. |
| cli-7 | open | S | `data/man/blueman-adapters.1` says the `adapter` arg selects the initial tab in `hci0` form, but `blueman/main/Adapter.py:74-76` matches tab keys and derives the page via `int(name[3:])`; any non-`hciN` value is silently dropped, and the positional has no CLI `help=` (`apps/blueman-adapters.in:25`). | Add `help=` to the positional stating the `hciN` format/behavior; align the man page. |
| cli-5 | open | S | `data/man/blueman-applet.1`, `blueman-manager.1`, `blueman-services.1` state "There are no options.", but each accepts `--loglevel`/`--syslog` via `create_parser`. Docs contradict behavior. | Replace "no options" with the actual flags. |
| cli-4 | open | S | `data/man/blueman-sendto.1` documents only `--device=ADDRESS`, but `apps/blueman-sendto.in:32-38` also ships `-d/--dest`, `-s/--source`, `-u/--delete` and a positional `FILE`. Man page is out of date vs `--help`. | Update the man page to list all options and the `FILE` positional. |

## product engineering

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|

## design thinking

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dsgn-1 | open | S | `blueman/main/Adapter.py:73-78` when `blueman-adapters <name>` names a nonexistent adapter, it logs "the selected adapter does not exist" to console but still opens the window on the default tab — a GUI-launched user gets no on-screen feedback that their argument was ignored (silent dead-end). | Show an in-window/infobar message (or a toast) and fall through to the first tab. |

## test / fuzz coverage

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| fuzz-3 | open | S | `blueman/DeviceClass.py:473-555` `get_major_class`/`get_minor_class`/`gatt_appearance_to_name` decode raw class-of-device and GATT appearance bitfields, untested. Hostile/boundary inputs: negative ints, values exceeding 16 bits, out-of-range minor indices, and appearance category boundaries around the reserved/invalid guards (:541-547). | Add `test/test_deviceclass.py` parametrized over major indices + overflow, each minor family in/out of range, and `gatt_appearance_to_name` at category edges plus a sweep asserting no `KeyError`/`IndexError` escapes. |
| fuzz-1 | open | M | `blueman/main/DhcpClient.py:25-77` has NO test file. `__init__` builds the client argv from `have()` across dhclient/dhcpcd/udhcpc; `_check_client` parses `poll()` status and reads `netifs[self._interface][0]`. Untested: client selection when several/none exist, argv assembly, poll-status branching, and the `KeyError`/`IndexError` when the bound interface is absent from `get_local_interfaces()`. | Add `test/main/test_dhcpclient.py` mocking `have`/`Popen`/`get_local_interfaces`; cover argv per client, run() raising when none found, double-run, poll 0/1/None, and hostile interface maps (missing key, empty tuple). |
| fuzz-2 | open | S | `blueman/Sdp.py:358-385` `ServiceUUID` is untested. `UUID(uuid)` raises `ValueError` on malformed input; `name`/`short_uuid`/`reserved` decode the 128-bit int and index `uuid_names[short_uuid]`. Untested: short vs full UUIDs, the all-zero case, Proprietary (non-reserved) UUIDs, unknown reserved short ids (KeyError→"Unknown"), and malformed/empty/garbage strings from the BlueZ wire. | Add `test/test_sdp.py` covering reserved short UUIDs, `int==0`, a non-Bluetooth-base UUID, an unknown reserved id, and a fuzz set of malformed strings asserting only `ValueError` escapes construction. |

---

## Open — parked

- **perf-12** (`ManagerProgressbar` instance cleanup) — the loop is GTK-widget-bound
  (`finalize()` touches builder/window/hbox/Stats) and is actually O(n), not O(n²); no real
  perf win and not unit-testable without a full Manager app. Park until reworked alongside the
  rob-1/rob-2 source-id fixes in the same file.
- **perf-14** (`GtkAnimation` per-animation timer) — the fix ("unify tick clock") is a
  shared-timer architecture change, not a low-risk edit, and can't reach genuine coverage
  headless. Park for a dedicated animation-scheduler change.
- **leg-1** (`check_bluetooth_status` `Gtk.Dialog.run()`/`.destroy()`) — `run()` is deprecated
  but still supported in GTK3. The function is a synchronous startup gate called by every entry
  point before the GLib main loop, and its result (via `exitfunc`) decides whether the app
  proceeds. A non-blocking response-signal rewrite must run a main loop and turn every caller
  into a continuation — a cross-file behavioural change on the bluetooth-enable path that cannot
  reach genuine coverage headless (needs a live dialog + main loop). Park for the GTK4 migration
  or a dedicated async-dialog change (overlaps leg-3, ux-6).
- **leg-2** (`create_menuitem` `Gtk.ImageMenuItem`) — deprecated but functional in GTK3.
  `create_menuitem` is the single chokepoint returning a `Gtk.ImageMenuItem`, consumed by ~20
  call sites (manager menu, status icon, plugins) that rely on the returned item's child being
  an `AccelLabel` with markup. The GTK3-supported replacement (`Gtk.MenuItem` + manual
  image/label box) changes the child structure and image handling — a visible UI change only
  validatable by running the GUI, so it can't meet the headless coverage bar. Park for the
  GTK4 migration alongside leg-4 (`ManagerMenu` `ImageMenuItem`).
- **leg-3 / ux-6** (`Sendto.py` deprecated `dialog.run()`/`.destroy()` → async response
  handlers) — three of the four `.run()` sites (`select_files`, `select_device`, the
  obex-start error dialog) are synchronous startup gates in `SendTo`/`Sender.__init__` whose
  return values drive control flow before the GTK main loop runs. Converting to the async
  response-signal pattern requires restructuring both `__init__`s into continuation-based
  flows, which cannot reach genuine coverage headless and carries high regression risk on the
  core send path. Park for the GTK4 migration (same rationale as leg-1). The other Sendto.py
  findings were fixed in fix/sendto-hardening.

## Audit picks deliberately rejected

- **wire-3** (`AppletStatusIconService` "has no public methods") — false positive. It is a
  signal-only `Gio.DBusProxy` for the `org.blueman.Applet.StatusIcon` interface. A proxy emits
  `g-signal` only for its own interface, so `Tray.py` needs this distinct proxy to receive
  `IconNameChanged`/`VisibilityChanged`/`ToolTipTitleChanged`/`ToolTipTextChanged`
  (`AppletMenuService` only delivers `MenuChanged` on the Menu interface). Deleting/inlining it
  would silence tray-icon updates. Kept; guarded by a test in `test/main/test_dbus_proxies.py`.
- **dead-1 / dead-2 / dead-3** (`set_proc_title`/`create_logger`/`create_parser` "no production
  callers") — false positives. The audit scanned `*.py` only and missed the entry-point
  templates: all three are imported and called by every binary in `apps/*.in`
  (`blueman-applet`, `blueman-manager`, `blueman-sendto`, `blueman-adapters`, `blueman-services`,
  `blueman-tray`, `blueman-mechanism`, plus `set_proc_title` in `blueman-rfcomm-watcher`).
  Deleting them would break startup of every executable. Kept and documented (doc-1); the
  related real issues were fixed instead: `create_parser` loglevel validation (cli-1),
  `create_logger` syslog fallback (plat-8), and `set_proc_title` non-Linux guard (leg-5).
