# Blueman Next — Implementation Plan (Phase 0 output)

Based on ARCHITECTURE_AUDIT.md and BUG_AUDIT.md. Production code has not been changed.

## Execution priority — user decision, 2026-10-15

Complete the redesign (Phases 1–8) before fixing existing bugs (Phase 9).
Existing audit findings remain deferred, including T-01 and B-01 through B-12;
they are not prerequisites for visual work. Preserve existing backend behavior.
Verify redesign changes and fix regressions introduced by them within the relevant
phase. Record pre-existing failures separately rather than expanding redesign scope.

## 0. Baseline (observation, not a bug-fixing phase)

- Use the existing CI unittest workflow in `.github/workflows/check.yml` as the
  baseline reference: configure with `./autogen.sh`, build with `make -C module`,
  then run `PYTHONPATH=module/.libs python3 -m unittest` with its dependencies available.
- Meson currently registers no tests; `meson test` is not a suite baseline.
- Record available results and environment blockers. Do not fix existing application
  bugs or test-suite defects as a prerequisite to the redesign.

## 1. Settled defaults and scope

- Keep GTK 3/PyGObject/Builder and the existing BlueZ backend. No GTK 4/libadwaita.
- Use `Blueman Next` as the provisional display brand. Final name is not a blocker.
- Preserve bus names, schemas, executable names, Python packages, plugins and units.
- Propose a complementary light palette in the first visual slice; iterate on the
  rendered result. Do not block engineering on a palette approval question.
- Leave plugin failure policies and all existing bug fixes for Phase 9.
- New appearance settings may be added to `org.blueman.general` with compatible
  defaults; do not expose unsupported system behaviors as nonfunctional controls.
- Runtime limitations in the bug audit remain explicit acceptance gaps. A redesign
  does not by itself satisfy automatic recovery or eliminate existing blocking calls.

## 2. Phase plan (mapped to CLIXAD.md §23)

Each phase: small reviewable commits, tests where feasible, no GTK 4, no libadwaita.

### Phase 1 — Branding foundation
- New `blueman/gui/theme/` package with a single brand module (display name,
  description, icon name, notification app name). Use one build-neutral branding
  input to generate Python constants and desktop/AppStream substitutions for both
  build systems; desktop files cannot consume a Python runtime constant directly.
  Brand constants used by the About
  dialog, window title, desktop files (generated from `.desktop.in`), and
  AppStream metadata. This is requested branding work; no separate B-08 fix is scheduled.
- Keep the `blueman` executable, `org.blueman.*` IDs, and `blueman` icon name.
- Documentation: `docs/BRANDING.md` explaining where the name lives.

### Phase 2 — Design system
- `data/themes/{dark,light,components,animations}.css` with the colour tokens from
  CLIXAD.md §5.1 as CSS named colours and an `alpha()` usage for borders.
- `blueman/gui/theme/DesignTokens.py` provides Python-side access for radar/status
  colours from the same palette source; avoid manually duplicated palettes. `ThemeManager.py` loads the CSS through
  `Gtk.CssProvider.load_from_path` / `add_for_screen`, switching on the
  new `org.blueman.general` appearance keys (system/dark/light and reduced motion).
  Scope CSS to the application; preserve desktop high-contrast and animation settings.
- Install the CSS with `install_data` in `data/meson.build`; the Python loader resolves
  the path from `Constants` (generated), extending its existing `BLUEMAN_SOURCE`
  mechanism. Update Autotools resource/Python lists and configure outputs as well;
  check staged installs from both builds, not only the source checkout.
- No CSS is loaded for the current window until Phase 3 is wired, so this phase cannot
  change the visible UI by itself.

### Phase 3 — Main window redesign
- New `data/ui/manager-main.ui` structure: `Gtk.HeaderBar` (title, Bluetooth status,
  search, settings), `Gtk.Paned` containing sidebar `Gtk.Box` and a `Gtk.Stack`
  (dashboard, scan, files, settings) and a right-hand inspector.
- Persist size via the existing `window-properties` key (`Manager.py:116`).
- Keep the toolbar/statusbar keys working during transition (`show-toolbar`,
  `show-statusbar`) until they are retired in a separate commit.
- Power switch in the sidebar reuses the existing `PowerManager` path and its
  reported state. B-06 remains deferred; redesign work must not claim to fix its
  existing asynchronous error-handling limitations.
- Layout min size 900×600, default 1400×850 for first use; preserve stored geometry.
  At narrow widths use an inspector drawer and a compact sidebar, rather than
  squeezing the dashboard between fixed 260px/340px panels. Verify at 900×600,
  1400×850 and 2× scale with long names and translated labels.
- Navigation routes to working existing actions/dialogs until the corresponding
  new page is ready. Never ship blank Files/Settings tabs as functional features.

### Phase 4 — Device cards
- Add card presentation over the existing model/controller first. Keep `Blueman.List`
  and its typed signals/model APIs available to existing consumers while adapting
  card selection to the backing TreeIter. Retain the legacy view until compatibility
  checks pass, then make cards the default visible presentation.
- Map selection/get/compare/filter conversions, hide-unnamed and sort preferences,
  clipboard and drag-and-drop actions, popup target selection and plugin menu items.
  Card “More” must target its device explicitly; pointer hit-testing on a hidden
  TreeView is not a valid compatibility strategy. Do not replace the model wholesale.
- Update only changed cards on property change (no full rebuild): key cards by device
  object path.
- Avatar categories from the existing device-class classification (`blueman/DeviceClass.py` and the existing
  ManagerDeviceList classification flow), not a new classifier.
- Battery shown only when BlueZ `Battery1` provides it.
- Do not port B-10 synthetic RSSI/TPL fallbacks into new cards. Display actual
  available readings or omit them; defer fixing the old implementation to Phase 9.

### Phase 5 — Device inspector
- Right-hand panel (340 px) bound to the selected card; actions reuse existing
  handlers (Connect, Disconnect, Pair, Send File, Audio, Forget with confirmation).
- Rename uses the existing rename dialog (`data/ui/rename-device.ui`).

### Phase 6 — Pairing and discovery
- Keep `BluezAgent` and `AuthAgent` unchanged; restyle `applet-passkey.ui` and the
  discovery view.
- Radar: `Gtk.DrawingArea` + Cairo, driven by `GLib.timeout_add` at ~30 fps, stopped
  when hidden, when Bluetooth is off, or when reduced motion is set.
- B-11 was not reproduced by the local signal probe; preserve existing transfer
  callbacks and validate real error presentation during Phase 8.

### Phase 7 — Animations
- `blueman/gui/theme/AnimationManager.py`: thin wrapper for timers and frame clock with
  a single "reduced motion" switch. Reuse `Gtk.Revealer`, `Gtk.Stack` transitions and
  `Gtk.Spinner`. Existing `blueman/gui/Animation.py` / `GtkAnimation.py` are reused or
  retired (GtkAnimation.py:200 FIXME is in this path).

### Phase 8 — Settings and transfers
- Settings dialog as `Gtk.Stack` + `Gtk.ListBox` with sections General, Adapter,
  Appearance, Notifications, Advanced. Only expose options that exist in the schema.
- OBEX transfer dialog: `Gtk.ProgressBar`, cancel, no simulated progress.

### Phase 9 — Bug fixing (after the redesign)
Order by priority (BUG_AUDIT.md): B-01 (P1), then B-02, B-04, B-05, B-06 (P2), then
confirmed remaining items. Reproduce each candidate before fixing and add a
meaningful regression test where feasible. B-05 is recovery work, B-08 is branding,
B-09 is a retained compatibility fallback, and B-11 is not currently reproduced.
Do not treat every audit row as an obligatory patch.

### Phase 10 — Production hardening
Performance check (idle CPU with radar stopped), accessibility pass, packaging, plugin
compatibility run, settings migration check.

## 3. First redesign milestone

Deliver Phases 1–4 incrementally: branding foundation, dark/light design system,
main window with header/sidebar/dashboard, and real device cards. Reuse existing
Bluetooth actions and preserve plugin contracts, including TreeIter/filter/selection
consumers; a row-dictionary adapter alone is insufficient.

Validate startup, rendering, selection, existing actions, and resource installation
for both Meson and Autotools. Record existing failures without fixing them. Continue
with inspector, pairing/discovery presentation, animations, settings, and transfers
(Phases 5–8), then address the existing bug backlog in Phase 9.

## 4. Rebranding plan

| Item | Where | Change in Phase 1 |
|---|---|---|
| Display name | `data/*.desktop.in`, UI titles, About | Via brand constant |
| Icon | `data/icons/hicolor/**/blueman*.svg` | Unchanged; new brand icon added alongside |
| AppStream | none found in `data/` (no `metainfo.xml` located) | Create `data/*.metainfo.xml.in` |
| Notifications | `Notification.py` app name | Via brand constant |
| Docs | `README.md`, `FAQ` | Add branding section; no rename |

## 5. Test strategy

- Unit: pure logic (device classification, search filter, power-state mapping).
- GTK: widget-level tests under `xvfb-run` where available; otherwise import smoke tests.
- D-Bus: use `dbusmock` (external) or a local fake object manager; never ship mock device
  data (CLIXAD.md §22).
- Manual checklist from CLIXAD.md §22 for each phase, recorded in the phase PR.

## 6. Internal identifier migration (separate, approval-gated)

Audit result (from ARCHITECTURE_AUDIT.md):

| Identifier | Used by | Migration risk |
|---|---|---|
| `org.blueman.Applet*`, `org.blueman.Mechanism`, `org.blueman.Services` | Applet, Manager, plugins, scripts | High — external callers |
| GSettings `org.blueman.*` (`data/org.blueman.gschema.xml`) | Every settings read | High — user config |
| Executables `blueman-manager`, `blueman-applet`, etc. | Desktop files, autostart | Medium |
| Python package `blueman` | Plugins, third-party | High |
| Plugin class names / `__plugin_info__` | `PluginManager`, user settings | High — saved plugin state |

Plan: keep all of these. Any future rename needs a compatibility alias on the bus, a
GSettings path migration with a one-time copy, and a deprecation release.

## 7. Breaking changes to document

None planned. Phase 4 must preserve the model/typed-signal and plugin action
contracts. Record any unavoidable external incompatibility explicitly before
changing it; a row-dictionary adapter does not establish compatibility.

## 8. Phase 0 results and remaining environment work

- Source audit revised against `67cea901`; fetched upstream main is the same commit
  (`0 0` ahead/behind, empty diff). Targeted upstream issue sampling is in BUG_AUDIT.md.
- Unconfigured `python3 -m unittest`: 258 tests, 37 failures, 83 errors.
- Configured baseline blocked at missing `autoreconf`, with additional development
  dependencies absent. See ARCHITECTURE_AUDIT.md §14; no application bugs fixed.
- No hardware, GUI, packaging or production-readiness claim is established yet.
  Restore build/test prerequisites in an appropriate environment before marking
  subsequent implementation slices verified. Do not fix old application defects
  merely to turn the baseline green.

## 9. Reviewable redesign slices and acceptance checks

These are planned slices, not completed work. Track execution status only in
INSTRUCTIONS.md. Split broad phases into the following bounded changes; each must
preserve existing working behavior and record baseline failures separately.

| Slice | Depends on | Main files/areas | Acceptance and verification |
|---|---|---|---|
| R1 Branding input and generated constants | Phase 0 | branding input, Constants.py.in, Meson/Autotools config | One input changes display identity in generated outputs; internal IDs unchanged; compare both generated outputs |
| R2 Desktop identity/resources | R1 | desktop templates, icons, AppStream, install lists | Installed launcher/About/notification names agree; validate desktop/AppStream metadata and staged resources |
| R3 Theme loader and preferences | R1 | theme package, CSS, schema, install lists | Dark/light/system persist; CSS parses on GTK 3; switching preserves high contrast and native focus; test source and installed paths |
| R4 Header/sidebar shell | R3 | manager-main.ui, Manager.py | Existing list and actions remain usable; no empty navigation destinations; verify saved geometry, shortcuts and narrow layout |
| R5 Card/model selection bridge | R4 | card/dashboard module, ManagerDeviceList, ManagerDeviceMenu | Card selects correct backing device without connecting; filtering/removal preserve valid selection; test model signals with fakes |
| R6 Card actions and grouping | R5 | card/dashboard module, menu/action adapters | Connected/paired/available groups are exclusive; actions reuse existing handlers; More preserves plugin items; test wrong-device and removal races |
| R7 Search and telemetry | R6 | dashboard/search, device presentation snapshots | Name/address search is case-insensitive and does no D-Bus work per keystroke; genuine battery including 0% shown, unknown values omitted; targeted tests |
| R8 Device inspector | R7 | inspector module, Manager integration | Selection updates identity/actions, missing values hidden, Forget confirms; keyboard and drawer checks at minimum width |
| R9 Pairing/discovery presentation | R8 | passkey UI, discovery presentation, notification presentation | PIN/passkey/confirmation/cancel remain user-controlled; real progress/error states; verify with mock agents and real devices when available |
| R10 Motion/radar | R9 | animation helper, radar, theme transitions | Respect GTK/application reduced motion; no new timer runs when hidden/disabled/destroyed; test source cleanup and inspect idle behavior |
| R11 Settings/adapter presentation | R10 | settings/adapter UI, appearance schema integration | Every exposed option works and persists; reuse adapter/plugin preferences; no unsupported startup/tray switches; keyboard and restart checks |
| R12 Transfer/notification presentation | R11 | send-dialog, receive notifications, presentation helpers | Existing send/receive/retry/cancel flows retained; actual progress/speed/ETA only; no duplicate notifications introduced; mocked and hardware checks |

R1–R7 comprise the first visible milestone (Phases 1–4). Inspect running screenshots
in both themes after R4 and R7. After R8–R12 verify the complete redesign before
starting the existing bug backlog. Do not replace a blocked GUI test with an import
smoke test and label visual behavior verified.

## 10. Compatibility and acceptance gates

- **Build/package:** compile both supported builds; stage installs in temporary
  destinations; verify CSS, Python modules, UI, icons, translations, schemas and
  desktop metadata. Keep GPL/copyright notices. No system installation required.
- **Functionality:** adapter switching, scan start/stop, pair/cancel, connect/disconnect,
  trust/block/remove, send/receive, audio profiles, network/serial/input services,
  tray and plugin settings. Record each as PASS/FAIL/BLOCKED/NOT RUN.
- **Accessibility:** keyboard-only navigation, Ctrl+K search, retained Ctrl+Q/Ctrl+W,
  clipboard shortcut, visible focus, accessible names, high contrast, reduced motion,
  and long translated text. Selection alone never triggers a connection.
- **Performance:** compare startup time, idle CPU and RSS against the same configured
  baseline/environment; report actual measurements rather than claim “fast.” Require
  zero new decorative timeout activity while hidden and zero property calls caused
  by typing/search. Profile slow property updates separately from existing B-03.
- **Data:** no production fake devices, pairing percentages or inferred battery.
  New display state must be tied to backend observations/operation callbacks.
- **Deferred limitations:** existing async power failures, blocking D-Bus access and
  BlueZ-loss exit behavior prevent unconditional final production acceptance until
  Phase 9/hardening. They do not block development of the redesign.

## 11. Internal migration inventory

Keep the policy IDs in `data/configs/org.blueman.policy.in`, rules in `blueman.rules`,
D-Bus activation/config files, systemd units, gettext domain and stored plugin names
in addition to the identifiers in §6. New display artwork can coexist with old icon
names. A future identifier migration must audit packaging and external consumers;
it is outside this redesign.
