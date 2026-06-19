# TODO

Project-wide rescan findings per AGENTS.md categories. Format: `id | status | effort | description | notes`.

Status: `open`, `in-progress`, `blocked`. Effort: `S` (≤1h), `M` (half-day), `L` (≥1 day).

---

## security

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| sec-1 | open | S | `blueman/plugins/applet/TransferService.py:181-186` interpolates the user-configured shared path into notification markup without escaping it. A path containing Pango markup can alter the fallback notification body and may be interpreted by notification daemons that support body markup. | Escape `shared-path` and the fallback path before formatting, or use a plain-text notification path. Add a regression test with `<b>`, `&`, and quote characters. |

## input validation / command safety

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cmd-1 | open | S | `sendto/blueman_sendto.py.in:20-28` builds a shell-style command line by wrapping file paths in double quotes and passing the joined string to `Gio.AppInfo.create_from_commandline`. A filename containing quotes or command separators can break argument boundaries when launched through the desktop shell parser. | Build a `Gio.AppInfo`/`Gio.Subprocess` invocation from an argv vector, or escape with GLib shell-quoting for every path. Add a regression test with spaces, quotes, and semicolons in filenames. Cross-ref test-1. |
| cmd-2 | open | M | `blueman/Functions.py:120-134` exposes `launch(cmd: str, ...)` as a command-line string API and sends it to `Gio.AppInfo.create_from_commandline`. Callers such as `blueman/plugins/manager/Notes.py:35` embed options in `cmd`, so argument boundaries depend on string parsing instead of an argv contract. | Replace or supplement `launch` with an argv-based helper (`program`, `args`, `files`) and migrate command-building call sites. Keep `system=True` uses explicit and reviewed. |

## data integrity

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| data-1 | open | S | `blueman/plugins/applet/TransferService.py:296-303` resolves incoming-file name collisions by prefixing only second-resolution time, then moves without rechecking the timestamped destination. Two same-named transfers completing in the same second can collide and overwrite/fail depending on platform semantics. | Generate a unique destination with an exclusive create/rename loop (`name`, `timestamp_name`, `timestamp_1_name`, ...), and test repeated same-second completions. |
| data-2 | open | S | `blueman/plugins/manager/Notes.py:32-35` creates a `.vnt` temporary file with `delete=False` and relies on the launched sendto process to delete it. If launch fails or the process never starts, the note body remains in `/tmp` indefinitely. | Delete the temp file when `launch()` returns false or raises; consider creating it in an app-owned temp directory with cleanup on startup. Cross-ref gov-5. |
| data-3 | open | S | `blueman/Functions.py:349-353` parses `/etc/os-release` lines with `line.split("=")`, so valid quoted values containing `=` are rejected and omitted from logged system info. | Use `split("=", 1)` and add a regression test with `PRETTY_NAME="Name=Variant"`. |

## performance

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| perf-1 | open | M | `blueman/main/ManagerStats.py:107` polls device stats via `GLib.timeout_add(1000, ...)` every second | switch to event-driven update or `timeout_add_seconds` |
| perf-3 | open | S | `blueman/gui/DeviceList.py:282-285` `clear()` iterates liststore calling `device_remove_event` per item → O(n²) | call `liststore.clear()` once, drop `path_to_row` in bulk |
| perf-4 | open | M | `blueman/bluez/Base.py:100` `device["Prop"]` issues sync `Properties.Get` DBus on UI thread | local prop cache + signal-driven invalidation |
| perf-5 | open | M | `blueman/bluez/Manager.py:115-149` `get_adapter_paths`/`get_devices` iterate `_object_manager.get_objects()` per call | cache, invalidate on object-added/removed |
| perf-9 | open | S | `blueman/main/DhcpClient.py:48-50,68` `subprocess.poll()` blocking in 1s `GLib.timeout` | use `Gio.Subprocess` + `wait_check_async` or `GLib.child_watch_add` |
| perf-10 | open | S | `blueman/gui/manager/ManagerMenu.py:53` creates Adapter proxies for all adapters in `__init__` | lazy-instantiate on selection |
| perf-11 | open | S | `blueman/main/Manager.py:161-164` `find_device()` linear scan over all objects | address-indexed dict |
| perf-13 | open | S | `blueman/main/Applet.py:93-118` plugin broadcast loop runs full plugin set per property change → O(plugins × props × devices) | debounce/batch property events |

## scalability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| scale-1 | open | M | `blueman/main/Manager.py:149-159` `populate_devices` emits per-device add signal serially | single batch signal |
| scale-2 | open | S | `blueman/main/PulseAudioUtils.py:216-218` PA subscribe callback fires unthrottled on rapid card changes | debounce |
| scale-3 | open | S | `blueman/main/BatteryWatcher.py:18` creates `Battery` per creation signal without dedup | check existence before create |

## caching strategy

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cache-1 | open | M | `blueman/bluez/Base.py:100-107` caches DBus properties only after a synchronous `Get`, and falls back to the cached value on later `GLib.Error` without freshness metadata. Callers cannot tell whether they received live state or stale state, and no cache invalidation policy is documented per property. | Make cache state explicit: update from `PropertiesChanged`, mark stale on bus errors, and expose/handle stale reads at call sites that need fresh state. Cross-ref perf-4, obs-13. |

## concurrency

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| conc-3 | open | S | `blueman/main/PulseAudioUtils.py:372-379` `weakref.proxy(self)` in callback silently no-ops if GC'd | hold hard ref or explicit lifecycle |

## code complexity

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cx-1 | open | M | `blueman/gui/manager/ManagerDeviceList.py:453` `row_update_event` 7-elif on property name | dict dispatch `{key: handler}` |
| cx-2 | open | M | `blueman/main/Manager.py:224` `simple_action()` 13-case match mixes routing + business logic | extract `{action: (handler, needs_device)}` table |
| cx-3 | open | L | `blueman/gui/manager/ManagerDeviceList.py:412-540` 4 coupled power-level methods (>100 LOC) | extract `PowerLevelMonitor` class |
| cx-4 | open | M | `blueman/main/PluginManager.py:132-174` `__load_plugin` ~43 LOC, 15+ conditionals (deps/conflicts/priority) | extract `PluginDependencyResolver` |
| cx-5 | open | M | `blueman/gui/manager/ManagerDeviceList.py:553` `tooltip_query` ~102 LOC nested conditions | extract `TooltipBuilder` |
| cx-6 | open | S | `blueman/main/Services.py:58` `on_query_apply_state` returns -1/bool mixed protocol | replace with `ApplyState` enum |

## code duplication

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dup-1 | open | M | `blueman/main/Applet.py:92-118` 8× identical plugin broadcast loops | `_broadcast(event, *args)` helper |
| dup-2 | open | S | `blueman/gui/manager/ManagerDeviceMenu.py:141-188` `connect_service`/`disconnect_service` duplicate nested success/error callbacks | extract async-DBus template |
| dup-4 | open | S | `blueman/gui/manager/ManagerDeviceList.py:498-540` `_update_power_levels` + `_disable_power_levels` duplicate bar lookup | extract `BarRenderer` |
| dup-5 | open | S | `blueman/gui/manager/ManagerDeviceList.py:655-677` `_set_cell_data` repeats if/elif for battery/rssi/tpl | polymorphic bar renderers |
| dup-6 | open | S | `blueman/main/Applet.py:78-90` `_on_dbus_name_appeared/_vanished` repeat plugin notify loop | `_notify_manager_state_change(state)` |
| dup-7 | open | S | `blueman/main/Sendto.py:47-55` 6× identical `connect_signal` boilerplate | `_setup_signal_handlers(source, handlers)` |
| dup-8 | open | S | `blueman/main/Services.py:86` bare `except:` with `# noqa: E722` | narrow to expected exceptions |

## API contract & compatibility

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| api-1 | open | S | `blueman/main/DBusProxies.py:91` exposes the Python proxy method as `dchp_client`, while the DBus method and interface are `DhcpClient`. The typo is now part of the local Python call surface and makes future refactors/API docs error-prone. | Add correctly spelled `dhcp_client()` as the public method, keep `dchp_client()` as a deprecated alias until callers/tests migrate, then remove the alias in a later cleanup. |
| api-2 | open | M | `blueman/Functions.py:133` uses `Gio.AppInfo.create_from_commandline` in a shared helper, but its API accepts one opaque command string plus separate `paths`. This makes it hard for callers to express portable argv semantics or safely pass non-file options without depending on GLib command-line parsing. | Define a stable internal process-launch contract around argv and file arguments; deprecate the string form after migrating users. Cross-ref cmd-2. |

## architecture/modularity/SOLID

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| arch-1 | open | L | `blueman/main/Applet.py:25-148` `BluemanApplet` is God object (init Manager, plugins, broadcasts, state) | extract `PluginBroadcaster`, `ManagerWatcher` |
| arch-2 | open | L | `blueman/main/Manager.py:37-363` `Blueman` mixes lifecycle, UI, device actions, settings | split into `ManagerUI`, `DeviceActionHandler`, `SettingsManager` |
| arch-3 | open | M | `blueman/main/PluginManager.py:176` `__getattr__` magic for plugin lookup breaks IDE/refactor | explicit `get_plugin(name)` accessor |
| arch-4 | open | M | `blueman/main/MechanismApplication.py:42-100` mixes timer, PolicyKit, plugin loading, DBus registration | extract `TimerManager`, `PluginLoader` |
| arch-5 | open | S | `blueman/main/MechanismApplication.py:15-39` Timer reads `BLUEMAN_SOURCE` env var for test mode | subclass `TestTimer` or inject duration |
| arch-6 | open | S | `blueman/main/PluginManager.py:139,200` raise bare `Exception(...)` | introduce `PluginDependencyError`, `PluginError` |
| arch-7 | open | S | `blueman/gui/manager/ManagerDeviceMenu.py:64-65` `__ops__`/`__instances__` class-level globals | DI or event-emitter |
| arch-8 | open | S | `blueman/gui/manager/ManagerDeviceList.py:334-351` UI-formatting `@staticmethod`s placed on liststore class | move to `DeviceDisplayFormatter` |

## decoupling

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dec-1 | open | M | `blueman/plugins/applet/TransferService.py:17` reaches into `parent.Plugins`/`parent.Manager` | DI via plugin interface or signal |
| dec-2 | open | M | `blueman/plugins/manager/Services.py:8` `ManagerPlugin` imports `ManagerDeviceMenu`, `MenuItemsProvider` (GUI layer) | event-based provider interface |
| dec-3 | open | S | `blueman/plugins/applet/AutoConnect.py:62` `self.parent.Manager.find_device()` reach-through | `parent.find_device_by_address(addr)` API |
| dec-4 | open | S | `blueman/plugins/applet/KillSwitch.py:147-149` direct `self.parent.Plugins.StatusIcon/PowerManager` access | optional plugin query w/ fallback |
| dec-5 | open | S | `blueman/plugins/manager/Services.py:82` plugin discovery via `ServicePlugin.__subclasses__()` | registry or `importlib.metadata.entry_points` |
| dec-6 | open | S | `blueman/plugins/AppletPlugin.py:32` hardcoded fallback icon name | constant + GSettings override |

## business/design patterns/DDD

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| pat-1 | open | M | `row_update_event`, `simple_action`, `_set_cell_data` all have type/key switch ladders | Strategy or dispatch-table |
| pat-2 | open | S | `on_query_apply_state` magic-return protocol | State enum (DDD value object) |
| pat-3 | open | M | Plugin lifecycle scattered (load/unload/deps/conflicts/state) | introduce `PluginLifecycle` state machine |

## reliability/correctness

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| rel-9 | open | S | `blueman/main/Services.py:86` bare `except: pass` hides errors | narrow exception types |
| rel-10 | open | S | `blueman/plugins/applet/TransferService.py:95-100` schedules removal of an allowed device but the timeout closure reads `self._pending_transfer` later instead of capturing the accepted address. A second pending transfer or cleared state can remove the wrong address or hit the assertion. | Capture `address` in the closure and remove it idempotently (`discard`-style) from the allowed list. Cross-ref sm-8. |
| rel-11 | open | S | `blueman/main/applet/BluezAgent.py:201-203` indexes `key[entered]` when displaying a passkey. If BlueZ reports `entered == 6` after all digits are typed, or an invalid value, the notification path raises `IndexError`. | Clamp `entered` to the valid range and render the fully-entered passkey without bolding a missing digit. Cross-ref test-2. |
| rel-12 | open | S | `blueman/plugins/BasePlugin.py:50` registers `weakref.finalize(self, self._on_plugin_delete)`. Passing a bound method keeps `self` strongly referenced by the finalizer, so plugin instances may not be collected and the delete hook is unreliable. | Register a module-level/static cleanup callback with weak state, or rely on explicit plugin unload and remove the finalizer. |

## observability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| obs-1 | open | S | `blueman/Functions.py:64,87` `print()` in `check_bluetooth_status()` exception/fallback | `logging.error(..., exc_info=True)` |
| obs-2 | open | S | `blueman/main/NetConf.py:93` `print()` for process termination | `logging.info` with binary/pid context |
| obs-3 | open | S | `blueman/main/Manager.py:62` `print()` in exception handler | `logging.error(..., exc_info=True)` |
| obs-4 | open | S | `blueman/bluez/obex/Manager.py:51,59,68,75` `logging.info(object_path)` lacks event/context | prefix with event name |
| obs-5 | open | S | `blueman/main/NetConf.py:340` silent `pass` on `BridgeException` | `logging.warning(...)` |
| obs-6 | open | S | `blueman/main/PluginManager.py:64,123` `LoadException` swallowed silently | `logging.warning` with plugin name |
| obs-7 | open | S | `blueman/gui/Notification.py:169` silent `ValueError` on notification hints | `logging.debug` unsupported hint |
| obs-8 | open | S | `blueman/main/Sendto.py:286` `logging.debug(e.message)` on `GLib.Error` | use `str(e)` |
| obs-9 | open | S | `blueman/gui/GtkAnimation.py:79` silent `ZeroDivisionError` on duration=0 | `logging.debug("Animation duration zero")` |
| obs-10 | open | S | `blueman/gui/GenericList.py:116` silent `ValueError` from `get_iter` | `logging.debug` invalid path |
| obs-11 | open | S | `blueman/main/DNSServerProvider.py:48` `GLib.Error` swallowed | `logging.debug("DNS lookup failed, using fallback")` |
| obs-12 | open | S | `blueman/plugins/mechanism/Network.py:46` exception only routed to error callback, no local log | add `logging.error` with trace |
| obs-13 | open | S | `blueman/bluez/Base.py:107` `GLib.Error` falls back to cached property silently | `logging.debug` cache fallback |
| obs-14 | open | S | `sendto/blueman_sendto.py.in:14,17,29,33` `print()` for user-facing messages | replace with `logging` where plugin host allows |
| obs-15 | open | S | `blueman/plugins/applet/AutoConnect.py:116-117` ignores automatic connection failures with `pass`, so failed auto-connect attempts leave no log trail and are hard to diagnose. | Log the target service/device and failure reason at debug or warning level, with rate limiting if needed. |

## wiring gaps

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|

_(none open)_

## unused functions/methods

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dead-1 | open | S | `blueman/Functions.py:217` `set_proc_title` in `__all__`, no production callers | delete |
| dead-2 | open | S | `blueman/Functions.py:239` `create_logger` in `__all__`, no production callers | delete |
| dead-3 | open | S | `blueman/Functions.py:264` `create_parser` in `__all__`, no production callers | delete |

## STRIDE

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| stride-1 | open | M | `blueman/main/DbusService.py:162-170` unhandled exceptions return full traceback in DBus errors, leaking internal paths to any caller | sanitize error messages on the bus; detailed traces to daemon log only |
| stride-4 | open | M | `blueman/main/MechanismApplication.py:50` if `POLKIT=False` at build, PolicyKit auth skipped silently (Elevation of privilege) | fail-closed; never silently skip authorization; log when disabled |

## data governance

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| gov-1 | open | M | `blueman/plugins/applet/RecentConns.py:127-139` device object paths + UUIDs stored unencrypted in GSettings | store only address/UUID; audit schema permissions |
| gov-2 | open | S | `blueman/plugins/applet/RecentConns.py:144` BT addresses (quasi-permanent IDs) logged via `logging.info` | redact/rate-limit address logging in production |
| gov-3 | open | M | `blueman/plugins/applet/NetUsage.py:40,64-65` per-device tx/rx stats persisted at `/org/blueman/plugins/netusages/{Address}/` reveal connection history + volume | document retention; add auto-expire option |
| gov-4 | open | S | `blueman/plugins/applet/RecentConns.py:120` user device aliases (may contain PII) stored plaintext | document plaintext storage; UI warning |
| gov-5 | open | S | `blueman/plugins/manager/Notes.py:32-35` can leave plaintext note bodies in temporary `.vnt` files when send launch fails. These notes are user-authored content and can include sensitive data. | Ensure temp-note lifecycle is owned by Blueman until a child process has definitely taken responsibility; clean stale `note*.vnt` files where safe. Cross-ref data-2. |

## multithreading

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| mt-1 | open | S | `blueman/gui/manager/ManagerMenu.py:96` `GLib.idle_add()` return value/source id ignored; no cleanup if parent destroyed | store source id, remove on teardown |

## watchdog

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| wd-1 | open | M | `blueman/main/PPPConnection.py:82-87` pppd spawned with no liveness monitoring; orphan pppd possible on error path | add `GLib.child_watch_add`, kill on cleanup |
| wd-2 | open | M | `blueman/main/PPPConnection.py:76` `cleanup()` only closes fd, leaves io_watch/timeout sources registered | remove all GLib sources in cleanup (overlaps rel-7) |
| wd-3 | open | M | `blueman/main/DhcpClient.py:49-50` two `timeout_add` sources, neither stored; `_check_client` keeps polling dead process after `_on_timeout` | store + `source_remove` both on exit (overlaps rob-3) |
| wd-4 | open | M | `blueman/plugins/mechanism/Rfcomm.py:14` rfcomm watcher Popen fire-and-forget, no PID tracking/liveness; only killed via grepped `ps` | track PID, supervise (overlaps sec-2, rel-8) |
| wd-5 | open | M | `blueman/services/meta/SerialService.py:75` `Popen([RFCOMM_WATCHER_PATH])` no exit/return-code monitoring; crash leaves rfcomm broken | child watch + restart/notify |
| wd-6 | open | S | `blueman/plugins/applet/PPPSupport.py:40` synchronous `Popen(['ps'])` blocks main loop until ps returns | use async `Gio.Subprocess` |
| wd-7 | open | M | `blueman/main/NetConf.py:122,190,235` Dhcpd/Udhcpd/DnsMasq Popen+communicate with no hang supervision | timeout-guard or async |
| wd-8 | open | S | `blueman/main/indicators/StatusNotifierItem.py:32-42` starts a repeating revision-advertisement timeout and discards the source id. The menu service cannot remove the source on unregister/teardown, so it can keep emitting after the tray path is gone. | Store the source id and remove it in an explicit `unregister`/delete path; add a test that teardown removes the source. |

## state machine

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| sm-2 | open | M | `blueman/main/PPPConnection.py:181-210` `on_data_ready` can run cleanup while `on_timeout` still pending → double `error-occurred` emit | explicit connection-state guard, single emit |
| sm-3 | open | L | `blueman/main/PPPConnection.py:213-224` `on_timeout` closure captures stale `command_id` if `send_commands` reused before fire | bind per-command state / cancel prior timeout |
| sm-4 | open | M | `blueman/main/DhcpClient.py:39-51` no state flag; `_check_client` + `_on_timeout` both call `querying.remove()` → possible `ValueError` | guard with done-flag, single removal (overlaps wd-3, rob-3) |
| sm-5 | open | M | `blueman/main/NetworkManager.py:38,69-70` `_statehandler` asserted not-None but state change can fire before assignment | assign handler before connect / null-guard |
| sm-6 | open | L | `blueman/plugins/applet/PowerManager.py:97,109` Callback timer source id not tracked; orphan timeout fires on GC'd object | store source id, remove in destructor |
| sm-7 | open | M | `blueman/main/NetConf.py:84-101` `DHCPHandler.clean_up()` reads/kills `_pid` with no guard; concurrent calls race / SIGTERM wrong pid | idempotent guard on `_pid` |
| sm-8 | open | M | `blueman/plugins/applet/TransferService.py:78-123` tracks only one `_pending_transfer` for authorization, but multiple incoming pushes can overlap before the user answers. A later request overwrites the pending state used by the first notification action. | Track pending transfers by `transfer_path`; bind notification callbacks to an immutable pending-transfer record. Cross-ref rel-10. |
| sm-9 | open | S | `blueman/plugins/applet/ShowConnected.py:86-92` schedules delayed `enumerate_connections()` calls on every manager-state-enabled event without storing/canceling the source. A fast state flap can let a stale enumeration update the icon after the manager is disabled. | Store the pending source id, cancel it on manager disable/unload, and ignore callbacks if manager state changed. |

## composition

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| comp-1 | open | M | `blueman/bluez/Base.py:11-26` `BaseMeta` metaclass couples object identity to DBus path via permanent instance cache | extract caching to registry/factory (overlaps conc-2) |
| comp-2 | open | M | `blueman/bluez/obex/Base.py:5` obex Base subclasses bluez Base, both override metaclass attrs; class-attr duplication | pass bus config to `__init__` instead of subclassing |
| comp-3 | open | S | `blueman/gui/manager/ManagerDeviceList.py:45` 4-level inheritance (Gtk.TreeView→GenericList→DeviceList→ManagerDeviceList) + parent-chain coupling | inject deps via constructor, prefer composition |
| comp-4 | open | M | `blueman/plugins/MechanismPlugin.py:8-12` copies parent methods (timer, confirm_authorization) into `__init__`; tight bind to concrete app | abstract plugin interface + DI |

## dependency

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dep-1 | open | L | `blueman/main/PulseAudioUtils.py:14-18` import-time `CDLL` load raises ImportError if libpulse absent, failing module | lazy loader + optional-support flag |
| dep-2 | open | L | `blueman/main/NetworkManager.py:9-12` import-time `gi.require_version` raises if NM bindings missing | move into lazy init try-block |
| dep-3 | open | L | `blueman/plugins/mechanism/RfKill.py:6-7` import-time `/dev/rfkill` check raises, blocks plugin discovery on systems without it | move check to `on_load()` |
| dep-4 | open | L | `blueman/plugins/applet/GameControllerWakelock.py:14-16,22-23` import-time GdkX11/X11 screen check raises | move platform check to `on_load()` |
| dep-5 | open | S | `blueman/main/Applet.py:10` wildcard `from blueman.Functions import *` obscures deps | explicit imports |
| dep-6 | open | S | `blueman/plugins/applet/NetUsage.py:8` wildcard import from `blueman.Functions` | explicit imports |
| dep-7 | open | M | `blueman/main/DNSServerProvider.py:12` hardcoded `RESOLVER_PATH="/etc/resolv.conf"` | configurable + DNSProvider abstraction (dup cfg-004) |
| dep-8 | open | L | `blueman/Functions.py:210` hardcoded PATH suffix `:/sbin:/usr/sbin` | use `shutil.which()` (dup plat-001) |

## adaptability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| adapt-1 | open | M | `blueman/gui/manager/ManagerDeviceMenu.py:225-242` hardcoded BlueZ error-string mapping with version-specific comments; breaks on newer BlueZ | parse error codes dynamically + version detect |
| adapt-2 | open | M | `blueman/main/Functions.py:104` (`blueman/Functions.py:104`) `time.clock_gettime(CLOCK_MONOTONIC_RAW)` fallback not portable | use `GLib.get_monotonic_time()` consistently |
| adapt-3 | open | M | `blueman/plugins/mechanism/Ppp.py:24` hardcoded `/dev/rfcomm{port}` template | inject device-path factory |
| adapt-4 | open | S | `blueman/main/DbusService.py` bus type hardcoded to SESSION; assumes single-user desktop | make bus_type configurable |

## extensibility

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| ext-1 | open | M | `blueman/main/PluginManager.py:132-174` load logic embedded in manager; hard to add plugin types/async loaders | extract LoadStrategy / load pipeline |
| ext-2 | open | M | `blueman/plugins/AppletPlugin.py:35-41` DBus service opt-in via `__dbus_iface_name__` is intricate | `@dbus_service` decorator / ServiceRegistry |
| ext-3 | open | L | `blueman/plugins/ServicePlugin.py:12-62` separate hierarchy from BasePlugin; no depends/conflicts declarations | unify to BasePlugin, add `__depends__`/`__conflicts__` |
| ext-4 | open | M | `blueman/services/meta/NetworkService.py` new service types must implement props; no extension hooks | ServiceRegistry + `@service_provider` |
| ext-5 | open | M | `blueman/main/indicators/IndicatorInterface.py` StatusIcon vs StatusNotifierItem hardcoded; no pluggable indicator backend | IndicatorBackend protocol via PluginManager |
| ext-6 | open | M | `blueman/plugins/applet/Menu.py` menu structure hardcoded; plugins can't extend menus without parent coupling | MenuRegistry / signal-based insertion |
| ext-7 | open | S | `blueman/gui/DeviceList.py:147-162` override hooks only; no registry for third-party extensions | signal-based hooks / extension protocol |

## legacy

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| leg-1 | open | M | `blueman/Functions.py:78` deprecated `Gtk.Dialog.run()`/`.destroy()` blocking pattern | non-blocking response-signal pattern |
| leg-2 | open | M | `blueman/Functions.py:189,200` deprecated `Gtk.ImageMenuItem` | migrate to `Gtk.MenuItem` + image |
| leg-3 | open | M | `blueman/main/Sendto.py:178,190,291,461` deprecated dialog `.run()`/`.destroy()` | async response handlers |
| leg-4 | open | M | `blueman/gui/manager/ManagerMenu.py:45,47` `Gtk.ImageMenuItem` in manager UI | migrate to `Gtk.MenuItem` |
| leg-5 | open | S | `blueman/Functions.py:226` raw ctypes `libc.prctl(15,...)` for proc title | document or guard non-Linux (relates dead-1) |
| leg-6 | open | S | `blueman/gui/GtkAnimation.py:200` FIXME `Gtk.render_background()` wrong colors | investigate + fix or document |
| leg-7 | open | S | `blueman/bluez/Device.py:22,29` `# type: ignore` on connect/disconnect masking signature mismatch | resolve override signatures |
| leg-8 | open | S | `blueman/bluez/Network.py:17,26` `# type: ignore` on connect/disconnect | resolve signatures |
| leg-9 | open | S | `blueman/main/indicators/GtkStatusIcon.py:44` `# type: ignore` on submenu enumerate | proper overload/typing |

## configuration

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cfg-1 | open | M | `blueman/Constants.py.in:22` `BLUEMAN_SOURCE` env var checked inline, undocumented feature flag | centralize in config module + document |
| cfg-2 | open | M | `blueman/main/MechanismApplication.py:25` idle timeout hardcoded (30s / 9999 dev) keyed on `BLUEMAN_SOURCE` | make configurable, document dev mode (overlaps arch-5) |
| cfg-3 | open | S | `blueman/main/NetConf.py:62,256` hardcoded `/var/run` PID path | use `XDG_RUNTIME_DIR`/`/run` (overlaps dep-11) |
| cfg-4 | open | M | `blueman/main/DNSServerProvider.py:12` hardcoded `/etc/resolv.conf`, precedence undocumented | document resolved-first precedence |
| cfg-5 | open | S | `blueman/main/DhcpClient.py:17-20` DHCP client search order hardcoded (dhclient/dhcpcd/udhcpc) | configurable list |
| cfg-6 | open | M | `blueman/plugins/services/Network.py` DHCP handler selection (dnsmasq/dhcpd/udhcpd) no user config, undocumented fallback chain | document + expose config |
| cfg-7 | open | S | `blueman/config/AutoConnectConfig.py:10` GSettings schema id hardcoded, duplicated across plugins | module constant |

## platform

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| plat-1 | open | M | `blueman/Functions.py:210` hardcoded `:/sbin:/usr/sbin` fallback (dup dep-8) | `shutil.which()` |
| plat-2 | open | M | `blueman/main/PPPConnection.py:83` hardcoded `/usr/sbin/pppd` | dynamic `have()` lookup |
| plat-3 | open | M | `blueman/main/NetConf.py:268,276` hardcoded `/sbin/iptables` | dynamic lookup |
| plat-4 | open | L | `blueman/main/NetConf.py:255` hardcoded `/proc/sys/net/ipv4` IP-forward, Linux-only | abstract, no non-Linux fallback |
| plat-5 | open | M | `blueman/plugins/applet/KillSwitch.py:59,87` hardcoded `/dev/rfkill`, silent fail without it | feature-detect + graceful degrade |
| plat-6 | open | S | `blueman/plugins/mechanism/RfKill.py:6` module-level `/dev/rfkill` check raises at import (dup dep-3) | move to `on_load()` |
| plat-7 | open | M | `blueman/plugins/applet/NetUsage.py:84,87` hardcoded `/sys/class/net` sysfs paths, Linux-only | abstraction + degrade |
| plat-8 | open | S | `blueman/Functions.py:256` hardcoded `/dev/log` syslog address | platform detect / fallback to stderr |
| plat-9 | open | M | `blueman/main/NetConf.py:24` `/proc/{pid}` cmdline check, Linux-only | abstract proc access |
| plat-10 | open | S | `blueman/services/meta/SerialService.py` hardcoded `/dev/rfcomm{port}` naming | abstract device node |

## data structure

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| ds-2 | open | M | `blueman/plugins/applet/NetUsage.py:261-268` linear liststore scan by address in `monitor_added` | address→iter dict |
| ds-3 | open | M | `blueman/plugins/applet/NetUsage.py:276-283` linear liststore scan by address in `monitor_removed` | address→iter dict |
| ds-4 | open | M | `blueman/plugins/applet/RecentConns.py:129-137` linear scan of `stored_items` by (adapter,address,uuid) | tuple-keyed dict |
| ds-5 | open | M | `blueman/bluez/Manager.py:160-164` `find_device()` scans all DBus objects, repeated Address lookups | cached device index (dup perf-11, scale) |

## vectorization

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| vec-1 | open | M | `blueman/main/Sendto.py:140-143` per-property-change loop over UUIDs for OBEX_OBJPUSH | set membership / `any()` |
| vec-2 | open | L | `blueman/bluez/Manager.py:138-149` `get_devices()` rescans all objects per `find_device()` | cache indexed by adapter, batch GetAll (dup perf-5) |
| vec-3 | open | L | `blueman/gui/DeviceList.py:281-289` `clear()` per-row `device_remove_event` + dict lookups | bulk clear, defer path_to_row cleanup (dup perf-3) |

## robustiness

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| rob-1 | open | M | `blueman/gui/manager/ManagerProgressbar.py:178` `timeout_add(41,pulse)` source id not captured; pulses after `stop()` | store + remove source id (overlaps perf-14) |
| rob-2 | open | M | `blueman/gui/manager/ManagerProgressbar.py:117` `timeout_add(timeout,finalize)` id discarded; double-finalize | capture + remove before re-call |
| rob-3 | open | M | `blueman/main/DhcpClient.py:49-50` two timeout sources never stored/removed (dup wd-3) | store ids, remove on exit |
| rob-4 | open | M | `blueman/gui/DeviceList.py:256` discovery progress timeout source not stored/removed | capture id, remove in `stop_discovery()` |
| rob-5 | open | S | `blueman/main/PPPConnection.py:182-197` OSError path may skip `source_remove(io_watch)` before cleanup → leaked source | remove source in except (overlaps rel-7) |
| rob-6 | open | S | `blueman/plugins/applet/NetUsage.py:79-80` Monitor `__del__` doesn't remove timeout source | guard + `source_remove(poller)` |
| rob-7 | open | M | `blueman/main/Sendto.py:351-378` `on_transfer_progress` divides by `spd` without re-guard after ZeroDivisionError | `if spd>0` guard + log |
| rob-8 | open | S | `blueman/gui/Animation.py:28-35` `start()` is not idempotent: calling it twice overwrites `self.timer` and leaks the first `GLib.timeout_add` source, so `stop()` can remove only the newest timer. | Return early if already started, or stop the existing source before starting a new one; add a start/stop source-id test. Cross-ref test-4. |

## ui / ux

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| ux-1 | open | M | `blueman/main/Sendto.py:310` blocking `time.sleep(1)` on UI thread during discovery stop | `GLib.timeout_add_seconds` |
| ux-2 | open | S | `blueman/gui/Notification.py:51` hardcoded notification size 350x50 | responsive sizing |
| ux-3 | open | S | `blueman/gui/manager/ManagerProgressbar.py:50` hardcoded progressbar 100x15 | flexible sizing |
| ux-4 | open | M | `blueman/gui/Notification.py:168-169` bare `except ValueError: pass` on hint set (dup obs-7) | log when fallback occurs |
| ux-5 | open | S | `blueman/gui/Notification.py:107-108` empty `add_action()` stub logs warning | implement or remove stub |
| ux-6 | open | M | `blueman/main/Sendto.py:178,188,291,461` blocking `dialog.run()` freeze UI (overlaps leg-3) | non-blocking response signals |
| ux-7 | open | S | `blueman/gui/manager/ManagerDeviceList.py:508` FIXME "horrible workaround" inadequate feedback | proper user feedback |
| ux-8 | open | S | `blueman/main/Manager.py:183` FIXME BlueZ stop/start not surfaced to user | notification/infobar on daemon loss |

## accessibility

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| a11y-1 | open | S | `blueman/gui/applet/PluginDialog.py:87-112` dynamically creates labels next to `Gtk.SpinButton`/`Gtk.Entry` controls but does not set mnemonic widgets or accessible label relationships. Screen readers and keyboard users get weaker context for plugin preference fields. | Use mnemonic labels (`use_underline`) where possible and set label/accessibility relationships for generated controls; add an accessibility smoke test for generated preference widgets. |

## i18n

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| i18n-1 | open | S | `sendto/blueman_sendto.py.in:46-50` hardcodes Nautilus/Caja/Nemo menu labels and tips in English, and `sendto/blueman_sendto.py.in` is not listed in `po/POTFILES.in`, so translators never see them. | Wrap file-manager extension labels/tips in gettext and add the generated/template source to extraction. |
| i18n-2 | open | S | `blueman/main/applet/BluezAgent.py:201-229` builds authentication notification sentences by concatenating translated fragments with device names, PINs, and markup. Translators cannot reorder the whole sentence or place punctuation naturally. | Use one format string per complete sentence/message with named placeholders, e.g. `%(device)s` and `%(passkey)s`, preserving markup escaping. |
| i18n-3 | open | S | `blueman/plugins/applet/TransferService.py:186` uses the action label `"Reset to default"` without gettext, so the fallback notification action is always English. | Wrap the action label in `_()` and ensure it appears in `po/POTFILES.in`. |

## documentation

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| doc-1 | open | S | `blueman/Functions.py:217,239,264` dead `set_proc_title`/`create_logger`/`create_parser` in `__all__` (see dead-1..3) | document or remove |
| doc-2 | open | M | `blueman/gui/GenericList.py` no module/class docstring | document TreeView wrapper + signals |
| doc-3 | open | M | `blueman/gui/DeviceList.py` class docstring missing; signals only in `__gsignals__` | document model + key signals |
| doc-4 | open | S | `blueman/main/Builder.py` class lacks docstring | document Gtk.Builder wrapper behavior |
| doc-5 | open | M | `blueman/gui/Notification.py` `Notification()` factory + bubble/dialog undocumented | document return-type selection |
| doc-6 | open | M | `blueman/gui/DeviceSelectorDialog.py` `DeviceRow`/`DeviceSelector` lack docstrings | document selector pattern |
| doc-7 | open | M | `blueman/gui/CommonUi.py` `ErrorDialog` lacks docstring; `excp` param undocumented | document exception UI |
| doc-8 | open | S | `blueman/gui/manager/ManagerProgressbar.py` class undocumented (cancellable/text params) | document progress lifecycle |
| doc-9 | open | M | `blueman/gui/GsmSettings.py` class lacks docstring | document GSM settings binding |
| doc-10 | open | M | `README` lacks plugin/dev API docs | document plugin loading + extension points |

## test coverage

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| test-1 | open | S | No tests cover `sendto/blueman_sendto.py.in` command construction for selected file paths. The quoting bug in cmd-1 would pass unnoticed for paths with quotes, semicolons, or leading dashes. | Add a small unit test around the file-list-to-launch-command path after extracting it into a pure helper. Cross-ref cmd-1. |
| test-2 | open | S | No tests cover `BluezAgent._on_display_passkey` boundary values for `entered`. `blueman/main/applet/BluezAgent.py:201-203` indexes `key[entered]`, so an out-of-range or fully-entered value can crash the agent notification path. | Add focused tests for `entered` values 0, 5, 6, and invalid values; clamp or render without bolding when all digits are entered. |
| test-3 | open | M | Incoming OBEX transfer authorization and completion paths in `blueman/plugins/applet/TransferService.py:78-123,286-329` have no focused tests for overlapping requests, allowed-device expiry, filename collisions, or failed final moves. Current coverage would miss data-1, rel-10, and sm-8. | Extract testable helpers for pending-transfer records and destination selection; add unit tests with mocked `Transfer`, `Session`, and notifications. |
| test-4 | open | S | No tests cover `blueman/gui/Animation.py` timer source lifecycle. The `start()`/`stop()` path can leak sources if `start()` is called repeatedly, and current tests would not detect it. | Add a focused test with mocked `GLib.timeout_add`/`source_remove` for idempotent start and complete cleanup. Cross-ref rob-8. |

## release & deploy engineering

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| releng-1 | open | S | `make_release.sh:3-7` archives `HEAD` using the latest tag name from `git describe --tags --abbrev=0`, without verifying that `HEAD` is exactly that tag or that the working tree is clean. A release tarball can be mislabeled with the previous tag or include unintended worktree attributes. | Require `git describe --tags --exact-match`, fail on dirty status, and print the commit/tag being archived. |
| releng-2 | open | S | `make_release.sh:9-16` produces `.tar.xz` and `.tar.gz` but no checksums or signatures. Downstream packagers/users have no release-integrity artifact from the script. | Generate SHA256 sums and optionally detached signatures as part of the release script, documenting the expected verification flow. |

## dependability

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| depend-1 | open | M | `blueman/main/NetConf.py:64-72` `DHCPHandler.apply` locks `dhcp` after a successful `_start` even when `_read_pid_file` returns `None` (daemon slow to write its pidfile; `DnsMasqHandler`/`UdhcpdHandler` don't reliably yield a pid in time). Later `clean_up` reads a now-absent pidfile, logs "Stale dhcp lockfile" and never kills the orphaned daemon — leaking a DHCP server bound to pan1. | Poll the pidfile with a bounded retry before locking; if no pid is obtained, treat the start as failed and tear down instead of locking. Cross-ref sm-7. |
| depend-2 | open | S | `blueman/main/NetConf.py:117-119` `DnsMasqHandler._start` appends `--dhcp-option=option:dns-server,{join(dns_servers)}` whenever `localhost:53` is reachable; if `DNSServerProvider.get_servers()` returned empty the option becomes a trailing-comma empty value, which dnsmasq rejects — the start fails entirely instead of degrading to "address but no DNS option". | Only append the `dns-server` option when `dns_servers` is non-empty. |
| depend-3 | open | S | `blueman/main/DNSServerProvider.py:29,102` `_get_servers_from_systemd_resolved`/`_subscribe_systemd_resolved` call `Gio.bus_get_sync(SYSTEM)` and `DBusProxy.new_for_bus_sync` with no error handling around bus/proxy acquisition (only the later `Get` at :48 is guarded). A briefly-unavailable system bus makes `__init__` raise and the whole provider fail rather than falling back to resolv.conf. | Wrap bus/proxy acquisition in try/except `GLib.Error` and degrade to the resolv.conf path. Cross-ref mem-2. |

## distributed systems

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dist-1 | open | M | `blueman/main/NetConf.py:366-374` `lock`/`unlock`/`locked` are plain `touch`/`unlink(missing_ok)`/`exists` on `/var/run/blueman-*` with no `flock` or atomic check-and-set. The mechanism is a system D-Bus service serving concurrent `EnableNetwork`/`DisableNetwork`/`DhcpClient` calls; two near-simultaneous `apply_settings` both see `locked()==False`, both enable forwarding, both append iptables MASQUERADE/FORWARD rules, and both start DHCP daemons on pan1 — duplicate rules accumulate and the shared `_dhcp_handler`/`_ipt_rules` class state corrupts. | Hold a real exclusive lock (`fcntl.flock` on the lockfile) across the whole apply/clean_up, or process mechanism requests strictly serially; make rule application idempotent (flush blueman rules before re-adding). |
| dist-2 | open | M | `blueman/main/NetConf.py:253,270,280` `_ipt_rules` is in-memory class state but the iptables rules it tracks live in the kernel and survive a mechanism restart (idle-exit after 30s, `MechanismApplication.py:25`). After re-activation `_ipt_rules` is empty while old MASQUERADE/FORWARD rules and the `iptables` lockfile persist; a later `clean_up`/`_del_ipt_rules` deletes nothing yet `unlock("iptables")`, and a new apply sees the stale lock and skips re-adding — leaving stale rules for the previous address. | Tag blueman rules with an iptables comment and flush-by-comment on apply; reconcile lockfile state against actual kernel rules at startup instead of trusting in-memory state. |
| dist-3 | open | S | `blueman/plugins/mechanism/Rfcomm.py:13-14` `_open_rfcomm` spawns a watcher per call with no dedup; two `OpenRFCOMM` calls for the same `port_id` start two `blueman-rfcomm-watcher /dev/rfcommN` processes, and `_close_rfcomm` kills only by matching the `ps` cmdline (can leave orphans or signal a recycled/foreign PID). | Before launching, scan for an existing watcher on that port and skip if present; track watcher PIDs in the mechanism rather than re-deriving from `ps`. Cross-ref wd-4, mem-1. |
| dist-4 | open | M | `blueman/main/NetConf.py:347-348` In `apply_settings` the dhcp branch runs `clean_up()` (unlocks `dhcp`) then `apply()` (re-locks). If `apply`'s `_start` raises `NetworkSetupError`, earlier locks/forwarding/iptables from the same call are already applied — leaving a partially-applied state (bridge up, forwarding on, rules present) with no DHCP and no rollback; the caller just propagates a generic error. | Wrap `apply_settings` in try/except that runs full `NetConf.clean_up()` on any failure so the system is left all-or-nothing. Cross-ref depend-1. |

## time & scheduling correctness

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| time-1 | open | M | `blueman/main/SpeedCalc.py:21` `calc()` keys elapsed-time/speed math on wall clock `time.time()`; an NTP step or manual clock change can skew the divisor across retained samples and produce erratic speeds (the zero-elapsed guard only catches exact ties/backsteps within the window). | Sample with `time.monotonic()` / `GLib.get_monotonic_time()`; a monotonic clock never steps. Distinct from ds-1 (log prune) and adapt-2 (clock_gettime portability). |
| time-2 | open | S | `blueman/main/Sendto.py:360` transfer-progress throttle `tm - self._last_update > 0.5` uses `time.time()`; a backward clock step stalls all speed/ETA UI updates until wall time catches up, a forward step fires every call. | Use `time.monotonic()` for `tm`/`self._last_update`. |
| time-3 | open | S | `blueman/plugins/applet/NetUsage.py:201` session duration `datetime.now() - fromtimestamp(config["time"])` is pure wall-clock; if the clock moved backward since the stored start, the delta is negative and renders nonsense durations. | Clamp negative deltas to 0 (or store a monotonic anchor) before formatting. |
| time-4 | open | M | `blueman/main/MechanismApplication.py:20-29` the idle-exit timer counts 1s `timeout_add` ticks (`self.time += 1` to 30) instead of comparing a monotonic deadline; GLib coalesces/delays timeouts under load or suspend, so the "30s idle" auto-exit drifts and can fire much later than intended. | Record `GLib.get_monotonic_time()` on activity and exit once `now - last >= 30s`, independent of tick count. Cross-ref cfg-2. |

## memory and cpu management

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| mem-1 | open | S | `blueman/plugins/mechanism/Rfcomm.py:17` `_close_rfcomm` shells out `ps -e o pid,args` and `communicate()` synchronously inside the privileged mechanism D-Bus method, blocking the mechanism main loop while it scans every process to find one watcher PID. | Track watcher PIDs (from `Popen` in `_open_rfcomm`) keyed by port and kill by stored PID instead of scanning `ps`. Cross-ref dist-3. |
| mem-2 | open | S | `blueman/main/DNSServerProvider.py:29-79` `_get_servers_from_systemd_resolved` issues a chain of synchronous `call_sync` D-Bus calls (Get DNS, then per-interface GetLink + DefaultRoute Get) with `-1` (infinite) timeout on the main loop whenever DHCP servers are resolved, scaling with interface count and able to hang indefinitely. | Use finite timeouts and/or move resolution off the main loop; cache across the `changed` signal instead of re-walking all links each call. Cross-ref depend-3. |
| mem-3 | open | S | `blueman/main/NetConf.py:239` `UdhcpdHandler._start` calls a blocking `sleep(0.1)` after spawning udhcpd to wait for the pid file, inside the mechanism process. Distinct from ux-1 (Sendto UI sleep). | Poll the pid file with a short non-blocking `GLib.timeout_add` loop instead of a fixed blocking sleep. |

## system design

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| sysd-2 | open | M | `blueman/main/PluginManager.py:92,117` plugin discovery uses `plugin_class.__subclasses__()` (import side effects) and mutates shared class attributes (`cls.__unloadable__ = False`); two PluginManager instances (applet vs mechanism) or a reload mutate shared class state, so load order/conflict resolution is global, not per-manager. | Register plugins explicitly into a per-manager registry and keep per-instance load flags off the class object. Cross-ref dec-5, ext-1. |

## CLI / option integrity

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| cli-1 | open | S | `blueman/Functions.py:273` `--loglevel` has no `help`, no `choices`; an unrecognized value (e.g. `--loglevel verbose`) silently coerces to WARNING with no error, so users get quieter logs than expected. Applies to all 7 entry points using `create_parser`. | Add `choices=[debug,info,warning,error,critical]` (case-insensitive) and `help=`; argparse then rejects bad values clearly. |
| cli-2 | open | S | `apps/blueman-mechanism.in:38,57-58` `-d/--debug` only logs "Enabled verbose output" and does nothing else; the level is driven by `--loglevel`, so `--debug` does NOT enable debug logging — a dead/misleading flag. | Make `--debug` set `log_level = logging.DEBUG`, or remove it and document `--loglevel debug`. |
| cli-3 | open | S | `apps/blueman-adapters.in:24` `--socket-id` (XEmbed) is undocumented — no `help=`, absent from `data/man/blueman-adapters.1` — yet plumbed into `BluemanAdapters(... socket_id)`. | Add `help=` text and document, or mark intentionally internal. |
| cli-4 | open | S | `data/man/blueman-sendto.1` documents only `--device=ADDRESS`, but `apps/blueman-sendto.in:32-38` also ships `-d/--dest`, `-s/--source`, `-u/--delete` and a positional `FILE`. Man page is out of date vs `--help`. | Update the man page to list all options and the `FILE` positional. |
| cli-5 | open | S | `data/man/blueman-applet.1`, `blueman-manager.1`, `blueman-services.1` state "There are no options.", but each accepts `--loglevel`/`--syslog` via `create_parser`. Docs contradict behavior. | Replace "no options" with the actual flags. |
| cli-6 | open | S | `data/man/blueman-adapters.1:1` `.TH` header is `BLUEMAN-SENDTO` (copy-paste), so `man blueman-adapters` shows the wrong title/section. | Fix `.TH` to `BLUEMAN-ADAPTERS`. |
| cli-7 | open | S | `data/man/blueman-adapters.1` says the `adapter` arg selects the initial tab in `hci0` form, but `blueman/main/Adapter.py:74-76` matches tab keys and derives the page via `int(name[3:])`; any non-`hciN` value is silently dropped, and the positional has no CLI `help=` (`apps/blueman-adapters.in:25`). | Add `help=` to the positional stating the `hciN` format/behavior; align the man page. |

## product engineering

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| prodeng-1 | open | S | `blueman/main/Sendto.py:61-63` aborts with a bare log "Error: No Adapters present" (no GUI dialog, no remedy) when no adapter is present; a user who launched sendto from a file manager's "Send To" sees nothing actionable. | Show a GTK error dialog telling the user to enable/plug in a Bluetooth adapter, mirroring `check_bluetooth_status`. |
| prodeng-2 | open | S | `blueman/main/Sendto.py:69` `--source` with an unknown adapter logs "Unknown adapter, trying first available" only to console and silently falls back; a CLI user who mistyped `-s` never learns their choice was ignored. | Print the fallback notice to stderr (or error out) instead of silently switching adapters. |

## design thinking

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| dsgn-1 | open | S | `blueman/main/Adapter.py:73-78` when `blueman-adapters <name>` names a nonexistent adapter, it logs "the selected adapter does not exist" to console but still opens the window on the default tab — a GUI-launched user gets no on-screen feedback that their argument was ignored (silent dead-end). | Show an in-window/infobar message (or a toast) and fall through to the first tab. |

## test / fuzz coverage

| id | status | effort | description | notes |
|----|--------|--------|-------------|-------|
| fuzz-1 | open | M | `blueman/main/DhcpClient.py:25-77` has NO test file. `__init__` builds the client argv from `have()` across dhclient/dhcpcd/udhcpc; `_check_client` parses `poll()` status and reads `netifs[self._interface][0]`. Untested: client selection when several/none exist, argv assembly, poll-status branching, and the `KeyError`/`IndexError` when the bound interface is absent from `get_local_interfaces()`. | Add `test/main/test_dhcpclient.py` mocking `have`/`Popen`/`get_local_interfaces`; cover argv per client, run() raising when none found, double-run, poll 0/1/None, and hostile interface maps (missing key, empty tuple). |
| fuzz-2 | open | S | `blueman/Sdp.py:358-385` `ServiceUUID` is untested. `UUID(uuid)` raises `ValueError` on malformed input; `name`/`short_uuid`/`reserved` decode the 128-bit int and index `uuid_names[short_uuid]`. Untested: short vs full UUIDs, the all-zero case, Proprietary (non-reserved) UUIDs, unknown reserved short ids (KeyError→"Unknown"), and malformed/empty/garbage strings from the BlueZ wire. | Add `test/test_sdp.py` covering reserved short UUIDs, `int==0`, a non-Bluetooth-base UUID, an unknown reserved id, and a fuzz set of malformed strings asserting only `ValueError` escapes construction. |
| fuzz-3 | open | S | `blueman/DeviceClass.py:473-555` `get_major_class`/`get_minor_class`/`gatt_appearance_to_name` decode raw class-of-device and GATT appearance bitfields, untested. Hostile/boundary inputs: negative ints, values exceeding 16 bits, out-of-range minor indices, and appearance category boundaries around the reserved/invalid guards (:541-547). | Add `test/test_deviceclass.py` parametrized over major indices + overflow, each minor family in/out of range, and `gatt_appearance_to_name` at category edges plus a sweep asserting no `KeyError`/`IndexError` escapes. |
| fuzz-4 | open | S | `blueman/Functions.py:166-181` `format_bytes` has a confirmed boundary bug and no test: strict `<` on both band edges means exact powers of 1024 fall through to GB — `format_bytes(1024)` returns `(9.5e-07, "GB")` instead of `(1.0, "KB")`; 1048576/1073741824 likewise mislabel. | Fix comparisons to `<=`/`>=` and add tests asserting exact boundaries 1024→KB, 1048576→MB, 1073741824→GB plus 0, sub-1024, and a huge value. |
| fuzz-5 | open | S | `blueman/Functions.py:340-356` `parse_os_release` (nested in `log_system_info`) splits with `line.split("=")` and is untested: a valid `PRETTY_NAME="Name=Variant"` raises `ValueError` and is dropped; comment/blank/`=`-less lines also untested. | Extract `parse_os_release` to module scope, use `split("=", 1)`, and test `KEY="a=b"`, comment/blank, and missing-`=` lines asserting graceful skip. Cross-ref data-3. |
| fuzz-6 | open | S | `blueman/Functions.py:147-154` `adapter_path_to_name` parses a D-Bus object path with greedy `re.search(r".*(hci[0-9]*)", path)` (zero digits allowed) and is untested; hostile/edge inputs (`/org/bluez/hci`, trailing `dev_..` segments, `prefix-hci99-suffix`, empty/None, no-`hci`) can yield surprising captures or `None`. | Add tests for normal `/org/bluez/hci0`, None/empty→None, no-`hci`→None, trailing segments, and multiple `hci` occurrences to pin the greedy behavior. |

---

## Open — parked

- **perf-12** (`ManagerProgressbar` instance cleanup) — the loop is GTK-widget-bound
  (`finalize()` touches builder/window/hbox/Stats) and is actually O(n), not O(n²); no real
  perf win and not unit-testable without a full Manager app. Park until reworked alongside the
  rob-1/rob-2 source-id fixes in the same file.
- **perf-14** (`GtkAnimation` per-animation timer) — the fix ("unify tick clock") is a
  shared-timer architecture change, not a low-risk edit, and can't reach genuine coverage
  headless. Park for a dedicated animation-scheduler change.

## Audit picks deliberately rejected

- **wire-3** (`AppletStatusIconService` "has no public methods") — false positive. It is a
  signal-only `Gio.DBusProxy` for the `org.blueman.Applet.StatusIcon` interface. A proxy emits
  `g-signal` only for its own interface, so `Tray.py` needs this distinct proxy to receive
  `IconNameChanged`/`VisibilityChanged`/`ToolTipTitleChanged`/`ToolTipTextChanged`
  (`AppletMenuService` only delivers `MenuChanged` on the Menu interface). Deleting/inlining it
  would silence tray-icon updates. Kept; guarded by a test in `test/main/test_dbus_proxies.py`.
