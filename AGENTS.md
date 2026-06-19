# Agents Behavior Guide

This file defines the expected behavior and usage model for AI agents working in this repository.

## Purpose

- Provide a standard set of guidelines for agent interactions.
- Ensure consistent behavior when using AI tooling in this workspace.

## General Agent Behavior

- Always be polite and concise.
- Prefer short, actionable responses.
- Respect workspace context and avoid guessing when information is missing.
- When making code changes, clearly describe what was changed and why.
- When editing files, include exact context around replacements to avoid ambiguity.

## Rules

- Don't assume. Don't hide confusion. Surface tradeoffs and ask the user when unclear.
- Write the minimum code that solves the problem. Avoid speculative or unneeded changes.
- Touch only what you must. Clean up only your own mess and leave the workspace cleaner than you found it.
- Define success criteria before making changes. Verify against those criteria and iterate until satisfied.
- Keep code complexity <= 10 for any new function, class, or method.
- Avoid code duplication and apply SOLID principles where practical.
- Document assumptions, constraints, and design intent in comments or commit notes when they matter.
- Prefer explicit, maintainable solutions over clever shortcuts.
- Propose business/design patterns and DDD only when they improve clarity or structure.
- ALWAYS record review findings in `TODO.md` — never report them only in chat. Any time you
  scan, review, audit, or "look for issues" (not just major changes), add each finding to the
  matching category table in `TODO.md` before/while reporting it.
- ALWAYS remove completed items from `TODO.md` — once a finding is implemented + tested + merged,
  delete its row from the table outright. No "shipped" sub-sections, no struck-through entries.
  `git log` is the durable record. Exceptions: the "Open — parked" section keeps open-but-deferred
  items with a why-not-now annotation; the "Audit picks deliberately rejected" section keeps the
  rationale so future passes don't re-pick the same items.
- When making major changes, rescan the whole project and create or update `TODO.md` with one
  table per review category defined below. Each table uses the format:
  `id | status | effort | description | notes`.
- Keep every `TODO.md` table sorted by the `description` column. Each description starts with the
  affected `file:line`, so sorting clusters findings in the same file together — letting related
  items be fixed in one batch. Re-sort a table whenever you add or edit its rows.

### Category definitions

Use the lens that fits the finding; when a category names a framework, cite the specific
framework/law in the finding's `notes`.

- **security** — injection boundaries (command, path traversal, D-Bus/IPC input) and
  privilege boundaries (the polkit mechanism, setuid/root helpers). Every code path that
  acts on untrusted input validates it first. Threat-model through complementary lenses
  and name the one used: **STRIDE** (Spoofing, Tampering, Repudiation, Information
  disclosure, Denial of service, Elevation of privilege) per data-flow boundary; the
  **OWASP ASVS** checklist where it maps; and **attack trees** to decompose a high-value
  target (gain root via the mechanism, spoof a device, intercept a connection) into
  concrete leaf attacks.
- **input validation / command safety** — network and device inputs are validated before
  they are used to build shell, `iptables`, AT, or D-Bus commands; no argument injection
  via embedded spaces/newlines; command arguments are passed as argv lists, never a
  split string.
- **data integrity** — in-memory/UI state (e.g. the device liststore) stays consistent
  with the underlying bluez/system state: no stale row points at a removed device, signal
  handlers keep derived state in sync on add/remove/rename.
- **data governance** — no private absolute paths (`/home/…`), secrets, or API keys are
  committed, with a guard (CI grep / pre-commit) enforcing it; logs minimize sensitive
  identifiers (BT addresses, object paths) to what is needed and never leak them beyond
  the local session.
- **reliability / correctness** — logic bugs under normal flow.
- **robustness / recovery** — kill-safety, atomic writes (write-temp-then-rename),
  partial-state recovery (a dying process or interrupted operation can't corrupt state or
  orphan a resource), and cleanup of orphaned resources.
- **dependability** — stays useful when a dependency, provider, or optional subsystem
  fails: graceful degradation, retry/backoff with timeout coverage, fallback chains that
  stop before they amplify damage or hide partial failure.
- **observability / operability** — failures are *surfaced*, not merely logged; every
  background mechanism exposes liveness + last result; D-Bus timeouts are sensible and
  logging is actionable. Assess via the three pillars (logs / metrics / health) scaled to
  a desktop app, and a silent-failure audit — enumerate every way the system can degrade
  with no user-visible symptom.
- **concurrency** — concurrency-correctness on shared state and coordination; guards
  against interleaved updates and double-submit.
- **multithreading** — thread-safety and thread-resource issues beyond concurrency:
  background-thread lifecycle, swallowed futures whose exceptions are never checked, lock
  granularity, and GLib main-loop vs worker-thread boundaries.
- **distributed systems** — multi-process coordination across the applet / mechanism /
  services split (even on one box): lock correctness, idempotent re-runs, shared-resource
  contention, and partial-write durability across processes.
- **watchdog** — liveness/stall detection for long-running operations (DHCP, PPP,
  transfers, scans): timeouts, heartbeats, progress-stall detection, and automatic
  abort/recovery semantics.
- **state machine integrity** — every lifecycle transition (connect/disconnect, adapter
  power, agent pairing, lock/unlock, transfer/download) guards illegal transitions,
  prevents terminal-state re-entry, and cleans up on every error path — not just the
  cancel path.
- **time & scheduling correctness** — elapsed-time math uses a monotonic clock; timeouts
  and intervals (D-Bus timeouts, autoconnect interval, speed sampling) are keyed so replay
  or clock skew never double-fires or stalls; guard zero/negative elapsed time.
- **platform** — cross-distro/runtime portability: POSIX-only primitives, signal
  handling, and version assumptions on GLib/GTK/PyGObject, bluez, and D-Bus availability;
  production-vs-local divergence.
- **performance** — bottlenecks on hot paths (device-list render, signal handling, repeated
  property reads).
- **scalability** — behavior as adapters, devices, batteries, and signal traffic grow.
- **N+1 / call efficiency** — avoid per-row repeated D-Bus property `Get` calls where one
  `GetAll`/cached read suffices; batch lookups; UI refreshes don't fan out one IPC round-trip
  per item.
- **caching strategy** — every cache declares key shape + size cap + invalidation trigger
  + a public reset hook; derived UI state invalidates on the source signal.
- **data structure** — right structures on hot paths: sets/maps for membership, no O(N²)
  dedup, no per-item re-parse where a cache belongs.
- **memory and cpu management** — peak memory, streaming vs materialization, and CPU-heavy
  work kept off the GLib main loop.
- **code complexity** — cognitive complexity ≤ 10; fat methods split into helpers.
- **code duplication** — shared logic (input validation, D-Bus read/write, command
  building) lives in one place, not copy-pasted across modules.
- **architecture / modularity / SOLID** — proper boundaries: GUI thin, business logic in
  services, D-Bus/system access behind the bluez layer, no logic buried in widget code.
- **system design** — end-to-end subsystem boundaries and feedback loops: whether the
  architecture preserves isolation, operability, and extension seams across module
  boundaries.
- **decoupling** — separation of concerns across module seams; the bluez layer, GUI, and
  plugins are independently testable.
- **composition** — prefer small collaborators and explicit composition over god
  objects, inheritance-heavy shapes, and copy-pasted registries when that reduces
  coupling.
- **dependency** — third-party and optional imports are justified, pinned sensibly, and
  degrade gracefully when absent; a vendor dependency sits behind an app-owned adapter
  rather than being imported/`new`-ed across the codebase.
- **configuration discoverability** — every runtime knob (GSettings / config) has a
  default, a typed accessor, documented deployment coverage, validation where needed, and
  tests for security-sensitive defaults.
- **API contract & compatibility** — D-Bus and other IPC surfaces are reviewed as
  compatibility artifacts, not just docs: introspection ⇄ implementation parity in both
  directions, the full error/signal surface declared, stable signatures, and breaking
  changes that are deliberate, named, and versioned.
- **CLI / option integrity** — command options, help text, and defaults match actual
  behavior across the `blueman-*` entry points; ignored or misleading flags are findings.
- **wiring gaps** — shipped classes, services, plugins, commands, or signal handlers that
  exist and pass tests but are not connected to the runtime path expected by docs or
  tests. A feature is "shipped" only when the dispatcher actually invokes it.
- **unused code** — public-shaped methods/handlers with no caller, no test, no view; each
  finding records keep / inline / delete.
- **unused functions/methods** — narrower grep-proven dead or test-only callable symbols
  (no leading `_`, imported by no production code), including `__init__` re-exports no
  caller pulls; each finding records delete / wire / intentionally keep in `notes`.
- **legacy / deprecation** — back-compat shims whose constituency is grep-proven gone are
  flagged to remove; still-live shims are recorded as "do not remove" with the live caller
  so a future pass doesn't re-pick them.
- **plugin extensibility** — advertised extension points (applet / manager / mechanism
  plugins) stay open through registries and documented contracts rather than closed
  `if`/`switch` dispatch or private-only hooks.
- **adaptability** — hardcoded assumptions that block change without a code edit: magic
  numbers, locale/timeout/path constants, and lookup maps that should be config or a
  documented invariant.
- **business / design patterns / DDD** — apply patterns only when they remove a concrete
  pain; a missing pattern is a finding only when a named pattern would clarify a real
  boundary or lifecycle.
- **release & deploy engineering** — the path from green CI to a healthy installed build
  is engineered, not improvised: CI gates fail closed and mirror reality (job ordering,
  smoke tests against the real build, pinned actions, reproducible builds from committed
  lockfiles), with a documented upgrade/rollback story for the meson + autotools
  packaging.
- **UI / UX** — GTK surfaces render without dead controls; empty/loading/error states are
  handled; keyboard-first flows work. Assess through the **Laws of UX**
  ([lawsofux.com](https://lawsofux.com/)) and cite the relevant law per finding (Fitts's
  Law, Hick's Law, Jakob's Law, Doherty Threshold, Miller's Law, etc.).
- **accessibility** — semantic widgets, ATK/ARIA on interactive controls, keyboard
  navigation, focus management, and sufficient contrast.
- **product engineering** — shipped-default sanity, setup/onboarding friction, actionable
  runtime failures, and docs-vs-behavior drift from an end-user perspective.
- **design thinking** — user-centered empty/loading/error states, recovery paths, and
  decisions grounded in observed user needs rather than internal convenience.
- **documentation** — `README`, man pages, and setup docs stay truthful: documented
  commands work as written and advertised features/flags match the code.
- **i18n** — UI strings route through the gettext catalog; no hard-coded English on user
  surfaces.
- **purpose** — mission alignment to a Bluetooth manager; scope-creep subsystems flagged.
- **test coverage** — new functions carry focused unit/feature coverage before merge
  (≥80% target in CI); critical paths — input validation, command building, D-Bus signal
  handling, device-list updates — carry focused tests.
- **test / fuzz coverage** — property/fuzz/adversarial coverage exists for parsers and
  command builders (`ps` output, AT/`iptables`/shell argument construction, network
  inputs), concurrency, and IPC contracts; counts toward the same coverage gate.

## File Editing

- Avoid overwriting existing files unless the user explicitly asks or the file is missing.
- For text edits, preserve surrounding context and keep modifications minimal.
- Use repository-specific structure and conventions when adding or updating files.

## Communications

- Use headings and bullets for readability.
- Highlight changed files and key points.
- Keep final answers brief and professional.

## References

- This workspace currently contains only a small Python utility script, so agent actions should remain lightweight and focused.
