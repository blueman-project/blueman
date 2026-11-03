# Blueman Next — Bug Audit (Phase 0)

Revised 2026-10-15 against `67cea9010c114f1fd9df966d52a53b0a7f68f47f`.
**Existing bugs are deferred until after the redesign. No fix was applied.**
IDs are retained from the initial audit, including corrected or unconfirmed entries.
“Static” means the code path was inspected; it does not mean a hardware reproduction.
A FIXME or deprecation alone is not proof of a functional defect.

Priority: P0 crash/data loss/security; P1 broken Bluetooth functionality;
P2 incorrect state/workflow; P3 minor UX. Environment prerequisites are separate.

## Summary

| ID | Priority | Evidence/status | Finding |
|---|---|---|---|
| T-01 | Environment | Observed; configured run blocked | Unconfigured tests fail on generated Constants and dbusmock |
| B-01 | P1 | Static; failure policy needs analysis | Plugin startup failures can terminate or propagate |
| B-02 | P2 | Static | Service constructor catches BaseException, logs and skips |
| B-03 | P2 | Static call paths traced | Synchronous D-Bus reads/construction reach GTK callbacks |
| B-04 | P2 | Static; visible impact unverified | Adapter name-vanished callback only logs |
| B-05 | P2 | Corrected | Manager shows error and exits; no automatic recovery |
| B-06 | P2 | Static; remote rejection not reproduced | Power writes have no completion/error callback |
| B-07 | P3 | Triage only | Duplicate adapter-removal warning is already guarded |
| B-08 | P3 | Branding inventory | Hard-coded product name; not independently a translation defect |
| B-09 | P3 | Compatibility constraint | Deprecated Gtk.StatusIcon remains necessary fallback |
| B-10 | P2 | Static | Failed link-level reads display synthetic RSSI/TPL bars |
| B-11 | — | Not reproduced by local signal probe | Exception-to-string signal conversion works locally |
| B-12 | P2 | Static | Discoverability timer survives adapter/manager loss |

## T-01 — Test prerequisites, not a confirmed application bug

Current `python3 -m unittest` attempt: **258 tests, 37 failures, 83 errors**.
Output contains missing `blueman.Constants` and `dbusmock`; log is
`/tmp/blueman-phase0-unittest.log` (temporary). Do not treat all these failures as
application regressions. Historical pytest/unittest counts in the initial audit
were from different invocations and are superseded for this session.

`./autogen.sh` was attempted and stopped at missing `autoreconf`. `autopoint`,
`cython3`, `xvfb-run`, and pkg-config development metadata for PyGObject/BlueZ
are also unavailable. The configured baseline is **BLOCKED**, not passed.

Reference `.github/workflows/check.yml`: install its prerequisites in an appropriate
build environment, configure with `./autogen.sh`, build `make -C module`, and run
`PYTHONPATH=module/.libs python3 -m unittest`. Its synthetic rfkill fixture belongs
in an isolated test environment, not on a host device node. Meson registers no
tests here. No suite changes or application fixes are prerequisites to redesign.

## B-01 — Plugin load failure isolation (P1, static)

`PluginManager.__load_plugin` constructs a plugin outside its load try/except,
logs exceptions from `_load`, calls `bmexit` for non-unloadable plugins, and
re-raises otherwise. The bulk startup loop catches only `LoadException`; the
named/user-action path handles other exceptions differently. Simply removing
`bmexit` does not ensure startup continues.

Fail-fast behavior for a required plugin may be intentional. Do not classify
required plugins using only the names DBusService and Menu: trace dependency
closure, direct accesses, initialization side effects, and rollback first.
Future tests should cover constructor failure, optional/required load failure,
dependents, partial initialization, and startup versus user-enabled loading.
Preserve existing behavior during redesign.

## B-02 — Service constructor catches BaseException (P2, static)

`Services.py` catches bare `except:` around `ServicePlugin` construction. It logs
with traceback and skips the plugin, including for KeyboardInterrupt/SystemExit.
Ordinary exceptions are not hidden from logs. Changing to `except Exception`
would narrow the catch but would not itself surface a warning in the UI.

Deferred tests: one failing constructor does not suppress healthy plugins;
SystemExit/KeyboardInterrupt are not intercepted by the proposed narrower handler.
An ordinary RuntimeError-only test would not distinguish old and new catch behavior.

## B-03 — Blocking D-Bus calls in UI paths (P2, static)

- `bluez/Base.py`: synchronous proxy construction, Properties.Get, and GetAll.
  `__getitem__` invokes Get, falling back to cached values only after failure.
- `ManagerDeviceList.row_setup_event` and `filter_func` read device properties
  during GTK population/refilter callbacks; these are confirmed UI call sites.
- `DeviceList` constructs Manager, Adapter and AnyDevice/AnyAdapter objects in
  the UI setup path. `bluez/Manager.py` constructs its object manager synchronously;
  `AnyBase.__init__` calls `bus_get_sync`.
- `DBusProxies.py` contains synchronous applet helpers used in startup/tray work.

No stall duration was measured. Deferred remediation must cover reads as well as
construction and preserve invalidation, object removal and error semantics.
New search/card rendering must use snapshots and incoming property changes,
not add D-Bus reads on each keystroke. Existing backend blocking remains a known
limitation until later fixes; do not claim the final performance bar is already met.

## B-04 — Adapter-window name loss (P2, static)

`BluemanAdapters._on_dbus_name_vanished` only logs; `_on_dbus_name_appeared`
also only logs. However, the object manager separately delivers adapter removal
and `on_adapter_removed` removes tabs. The initial assertion that nothing in the
UI changes was too strong. Reproduce loss/reappearance with an object manager
before specifying a recovery fix. Expected future check: no stale actionable tab
and correct reconstruction after a restart.

## B-05 — Manager exits after BlueZ loss (P2, corrected)

The initial “not communicated” claim is false. `Manager.on_dbus_name_vanished`
hides the window, displays “Connection to BlueZ failed” in an ErrorDialog, destroys
the dialog, and calls `quit()`. The FIXME does not describe implemented recovery.

Automatic recovery is a future behavior change, not just an infobar text fix.
It needs ownership/cleanup of the old list, menus, stats, signals, and outstanding
operations before recreating them. During redesign retain/document current exit
behavior. Test restart recovery only when that deferred behavior is implemented.

## B-06 — Power write result is not observed (P2, static)

`PowerManager.set_adapter_state` calls `adapter.set('Powered', state)` and immediately
sets `self.adapter_state = state`. `Base.set()` queues an asynchronous Properties.Set
with no completion callback. A remote rfkill/BlueZ rejection therefore does not
reach this surrounding exception handler. Contrary to the original diagnosis,
the requested state can be recorded before success is known. Later Powered signals
can reconcile state, but a rejected write need not produce such a signal.

Deferred fix design: observe asynchronous completion/errors, reconcile actual
adapter properties, handle partial multi-adapter success, and clear pending state
on all outcomes. Returning a synchronous boolean or narrowing this catch alone
cannot solve the problem. Regression scenarios: rejection without a property
signal, success, adapter disappearance and mixed results across adapters.

## B-07 — Repeated removal warning (P3, triage only)

`DiscvManager.on_adapter_removed` already handles `adapter is None` without
dereferencing it. A FIXME and warning are not evidence of a functional failure.
Determine duplicate event origins before suppressing logs. Timer cleanup is B-12.

## B-08 — Product-name centralization (P3, branding inventory)

`ShowConnected.py` hard-codes `Blueman` in a tooltip. Centralizing display identity
belongs to the requested branding work; product names need not be translated merely
because they are literals. Do not schedule a separate existing-bug fix in this phase.
Preserve executable, schema, bus and plugin identifiers.

## B-09 — Gtk.StatusIcon deprecation (P3, compatibility constraint)

`main/indicators/GtkStatusIcon.py` is a fallback alongside StatusNotifierItem.
Deprecation alone is not a user-visible bug. Preserve both and test desktop-specific
tray behavior during hardening; do not remove the fallback as a “fix.”

## B-10 — Synthetic link-level bars (P2, static)

`ManagerDeviceList._update_power_levels` sets RSSI/TPL to 100 when `cinfo.failed`
and to 50 on individual read failures. These are presentation fallbacks, not actual
measurements. Battery uses a separate Battery1 Percentage value.

Defer correction of the old implementation. For the new card/inspector contract,
only display genuinely available telemetry and omit unavailable readings; do not
copy fallback bars as real RSSI. This is required by the redesign's no-fabrication
rule. Future regression test: failed read displays unavailable, not a percentage.

## B-11 — Suspected Sendto signal type mismatch (not reproduced)

The concrete producer is `bluez/obex/ObjectPush.py`: `transfer-failed` declares a
string parameter but emits a BluezDBusException. `Sender.on_transfer_failed` accepts
a string. `Transfer.error` carries no arguments and matches the optional default
message in `Sender.on_transfer_error`.

A standalone local GObject probe using the same string signal declaration emitted
an Exception object successfully; the callback received its string value. Thus the
suspected type mismatch is not a verified failure on this runtime. No production
module was patched and no OBEX operation was executed. Revisit only with a failing
version-specific reproduction; do not schedule a speculative fix.

## B-12 — Discoverability timeout survives adapter loss (P2, static)

`DiscvManager.on_adapter_property_changed` creates a repeating timeout calling
`on_update`, which always returns True. `on_manager_state_changed(False)` clears
the adapter and hides the item but does not remove the timer. Removing the selected
adapter likewise calls init/update without cancelling it. `on_unload` and some
property branches do remove the source.

The original “callback references stale adapter” description was inaccurate:
`on_update` touches the menu item/countdown, not the adapter. The verified concern
is continued timer work and stale menu state after loss, unless a separate property
event happens to cancel it. Deferred test: activate countdown, remove adapter/BlueZ
without a Discoverable/Powered change, then assert no source remains after cleanup.

## Upstream issue sampling and comparison

Local HEAD and fetched upstream main both equal
`67cea9010c114f1fd9df966d52a53b0a7f68f47f`; ahead/behind is `0 0`, with an empty
tree diff. No upstream fixes were imported. Issue sampling on 2026-10-15:

- [#1838: notification plugin state and manager callback report](https://github.com/blueman-project/blueman/issues/1838)
  concerns Blueman 2.2.4 and is closed. Use as a persistence/restart test scenario,
  not evidence that this checkout is affected.
- [#1864: manager launch from tray](https://github.com/blueman-project/blueman/issues/1864)
  is relevant to launch/row-animation regression coverage; local applicability
  was not reproduced.
- [#2888: rfkill authorization report](https://github.com/blueman-project/blueman/issues/2888)
  was located in search, but its opened page did not expose enough issue content
  to validate a local root cause. Keep as a reference, not a verified finding.

This is a targeted sample, not an exhaustive review of every issue or historical fix.

## Remaining verification

Configured test suite, actual Bluetooth devices, desktop/tray variations, pairing
cancellation/races, transfer retry/cancel paths, audio/network/serial profiles,
third-party plugin contracts and full restart/shutdown ordering remain unverified.
The inspected Sendto constructor also contains `time.sleep(1)` while stopping
scan, and empty-file handling continues after emitting failure; these are follow-up
triage observations, not fixes or claims of a complete Sendto correctness audit.
