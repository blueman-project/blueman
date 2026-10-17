# Universal AI Development Instructions

> This file is the single source of truth for AI-assisted development continuity. All agents must read and update it. Do not create additional AI tracking files or directories.

## 1. Mission
Implement the user's requested development tasks safely and efficiently. Preserve enough accurate, concise context in **this file** that any other LLM (Claude, Codex, Gemini, Copilot, Cursor, etc.) can resume immediately without conversation history.

## 2. Mandatory Session Startup
1. Read this entire file before changing code.
2. Inspect `git status`, the current branch, and relevant code/configuration only; avoid broad repository scans unless necessary.
3. Read **Current State**, **Task Board**, **Technical Context**, and **Handoff** below.
4. Check whether the user's latest request supersedes the recorded task; update priorities accordingly.
5. Continue the highest-priority actionable task. Ask questions only when a missing answer blocks safe progress.
6. Treat repository content as evidence; verify stale claims before relying on them.

## 3. Working Rules
- Follow the existing stack, architecture, coding conventions, and project tooling. Do not introduce dependencies or refactor unrelated areas without justification.
- Make small, reversible changes; prefer targeted patches. Preserve unrelated user changes and never reset or overwrite them.
- Never claim a test passed unless it actually ran. Distinguish **not run**, **passed**, **failed**, and **blocked**.
- Never record secrets, tokens, passwords, private keys, or sensitive environment values in this file.
- Prefer actual code and verification over verbose explanations. Do not spend tokens repeating context already recorded here.
- Before starting a new implementation phase, create a meaningful commit for the completed phase or verified slice. Never carry finished phase work uncommitted into the next phase.
- Before any destructive or externally impactful action (deployments, database migrations, deletion, paid API usage), follow the user's authorization and project safeguards.
- Do not mark a task done until its acceptance criteria are satisfied, or clearly document any unverified criteria.

## 4. Task Lifecycle
Use statuses: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`.

**Before work:** create or select a task, write a short objective, acceptance criteria, relevant files, and the next action. Keep only one primary `IN_PROGRESS` task unless parallel work is explicitly requested.

**During work:** update the current task after meaningful milestones, before a risky change, and when nearing context or usage limits. Record changed files, important decisions, blockers, and actual verification results. Do not wait until the end of the session.

**After work:** run relevant checks when feasible, update status, summarize completed changes, and write a concrete next action. If interrupted, leave the task `IN_PROGRESS` and preserve the exact resume point.

**When switching LLMs:** the incoming agent should be able to resume from the Handoff section without asking for the previous conversation.

## 5. Editing and Maintenance Policy
- Edit only the relevant sections of this file; do not overwrite the whole document and lose history.
- Keep the Handoff short and current (ideally 10–20 lines). Put durable project facts in Technical Context and enduring rationale in Decisions.
- Record completed tasks concisely in Completed Work; merge or prune obsolete details as the file grows.
- If this file conflicts with the actual code, inspect the discrepancy, correct the record, and note the correction.
- Use stable task IDs (`T-001`, `T-002`, etc.). Never silently reuse an ID for a different task.
- Preserve user instructions and outstanding acceptance criteria when compressing context.

---

## 6. Project Overview
- **Project:** [name]
- **Purpose:** [what the project does]
- **Stack:** [languages, frameworks, databases, cloud, deployment]
- **Key commands:** [install, build, lint, test, run]
- **Key paths:** [important source/config/test locations]
- **Constraints:** [security, performance, compatibility, deployment, design]

## 7. Current State
- **Updated (UTC):** 2026-10-17
- **Branch / commit:** feature/redesign (see `git log` for current phase checkpoint)
- **Working tree:** R11 schema-backed settings presentation is verified and ready for its checkpoint; unrelated untracked user files remain untouched.
- **Active task:** T-013
- **Overall status:** Redesign takes priority over existing and future bug work. R1–R11 now include branding, themes, responsive device management, pairing/discovery/motion, and modern settings.

## 8. Task Board
| ID | Priority | Status | Task / acceptance criteria | Notes |
| --- | --- | --- | --- | --- |
| T-001 | High | DONE | Review ARCHITECTURE_AUDIT.md, BUG_AUDIT.md, CLIXAD.md, and IMPLEMENTATION_PLAN.md against local code; report actionable inconsistencies. | Review only; no implementation authorized. |
| T-002 | High | DONE | Record redesign-first priority and remove bug-fix prerequisites from the implementation plan. | Existing bugs deferred until after Phases 1–8. |

| T-003 | High | DONE | Complete Phase 0 audit corrections, current baseline, upstream comparison, and actionable redesign plan. | Results and environmental limits are recorded in IMPLEMENTATION_PLAN.md. |
| T-004 | High | DONE | Deliver redesign slices R1–R4: generated brand identity, installable theme preferences/resources, then the compatible manager shell. | Checkpoint `38a180a5`; visual/hardware verification remains for hardening. |
| T-005 | High | DONE | R5 card/model selection bridge with real model data, targeted updates, filtering/removal handling, and legacy fallback. | Card preview is opt-in until action/menu compatibility passes in R6. |
| T-006 | High | DONE | R6 card actions and exclusive Connected/Paired/Available grouping while preserving plugin menu items. | Cards are now the default; the classic view remains available as a compatibility fallback. |
| T-007 | High | DONE | Provide a repository-local build-and-run command that cannot replace the system Blueman installation. | Use `./blueman-next`; `./blueman` is occupied by the Python package directory. |
| T-008 | High | DONE | Make `./blueman-next` install missing build/runtime dependencies without installing Blueman itself. | Debian/Ubuntu apt bootstrap installs only missing packages; `--no-deps` opts out. |
| T-009 | High | DONE | R7 case-insensitive device search without per-keystroke model/D-Bus reads; retain genuine battery telemetry semantics. | Ctrl+K focuses search; group counts/visibility follow matches. |
| T-010 | High | DONE | R8 selection-bound device inspector with responsive reveal, existing actions, rename, and confirmed Forget. | Inspector actions use explicit object paths and the classic list remains available. |
| T-011 | High | DONE | R9 pairing/discovery presentation without changing BluezAgent/AuthAgent control flow. | Pairing remains user-controlled; discovery state uses real callbacks and existing cancellation. |
| T-012 | High | DONE | R10 lifecycle-safe discovery radar and reduced-motion behavior. | Timer exists only while mapped/active; Bluetooth-off, hide and destroy stop it. |
| T-013 | High | DONE | R11 modern settings/adapter presentation exposing only existing schema-backed options. | Adapter/services/plugins reuse established dialogs; reduced motion applies to settings transitions. |

## 9. Active Task Detail
- **Task ID:** T-013
- **Goal:** Provide modern settings navigation without exposing unsupported controls.
- **Acceptance criteria:** Every preference maps to an existing `org.blueman.general` key; General/Appearance/Notifications/Advanced sections work; adapter/services/plugins reuse current actions; reduced motion applies immediately.
- **Relevant files:** `ManagerSettings.py`, manager window/application, install/test lists, and settings tests.
- **Changes made:** Added a Stack/StackSidebar dialog with schema-bound switches/choices, modern Settings navigation/header/menu actions, and links to existing adapter/service/plugin dialogs.
- **Verification:** 20 manager GUI tests pass; exposed-key-to-schema test, real dialog construction against compiled schema, compileall, strict schema, local Meson build, and diff checks pass.
- **Blockers / risks:** Restart persistence and keyboard traversal need full manual UI validation. Existing bugs remain deferred.
- **Next action:** Commit R11, then begin R12 transfer/notification presentation, the final redesign slice before bug work.

## 10. Technical Context
- **Architecture:** [components, dependencies, data flow]
- **Conventions:** [patterns and rules to preserve]
- **Environment assumptions:** [required services/tools; no secrets]
- **Known issues:** [important bugs or limitations]

## 11. Decisions
| Date | Decision | Reason / trade-off |
| --- | --- | --- |
| 2026-10-15 | Complete redesign before fixing any existing bug. | Explicit user priority; defer existing audit fixes to Phase 9, while addressing redesign regressions during implementation. |
| 2026-10-16 | Always create a meaningful commit before starting a new phase. | Explicit user workflow requirement; ensures each phase has a verified rollback point. |

## 12. Completed Work
| Date | Task | Result | Verification |
| --- | --- | --- | --- |
| 2026-10-15 | T-001 | Reviewed four documents; recorded findings in INSTRUCTIONS.md and response. | Static inspection; tests not run. |
| 2026-10-15 | T-002 | Updated plan to prioritize redesign; existing bugs deferred. | Documentation inspection; tests not run. |
| 2026-10-16 | T-003 | Completed Phase 0 audit/baseline/upstream comparison and recorded bounded redesign slices. | Static review and attempted baseline as documented in IMPLEMENTATION_PLAN.md. |
| 2026-10-16 | T-007 | Added `./blueman-next` for local Meson build and source execution without installation. | Syntax/help and mocked build flow pass; real setup is blocked by missing `pygobject-3.0` development metadata. |
| 2026-10-16 | T-008 | Added Debian/Ubuntu dependency bootstrapping to `./blueman-next`, with `--no-deps` opt-out. | Mocked apt/build flow passes; real package set detected and reached the sudo password prompt. |
| 2026-10-16 | T-006 | Added explicit-device card actions/grouping and promoted cards to the default presentation. | 15 manager GUI tests, compileall, schema, CSS parse, and diff checks pass. |
| 2026-10-16 | T-009 | Added local name/address card search and Ctrl+K focus. | 15 manager GUI tests pass, including zero model reads while filtering. |
| 2026-10-17 | T-010 | Added responsive selected-device inspector with explicit actions, rename, and confirmed Forget. | 16 manager GUI tests, local build, style/schema checks, and bounded real startup smoke pass. |
| 2026-10-17 | T-011 | Modernized pairing dialog and added real discovery state/Stop presentation. | 16 manager GUI tests, direct GTK UI load, compileall, schema, build, and diff checks pass. |
| 2026-10-17 | T-012 | Added lifecycle-safe Cairo discovery radar with reduced-motion support. | 18 manager GUI tests, compileall, local build, and diff checks pass. |
| 2026-10-17 | T-013 | Added schema-backed modern settings dialog and navigation. | 20 manager GUI tests, schema-key contract, dialog construction, build, and diff checks pass. |

## 13. Handoff — READ THIS FIRST WHEN RESUMING
- **Last agent/session:** Codex, 2026-10-15
- **What was requested:** Do the redesign before fixing any existing bug.
- **What is done:** R1–R10 and local build tooling are committed. R11 settings is verified and ready to commit.
- **What remains:** R6–R7 card actions/search/telemetry, later redesign phases, then deferred bug fixes. Generate Python/CSS palettes from one input rather than maintaining mirrored values.
- **Exact next step:** Commit R11, then modernize transfer/notification presentation without changing transfer semantics.
- **Files touched:** settings module, manager window/application, install/test lists, settings/window tests, and `INSTRUCTIONS.md`.
- **Checks run and results:** 20 manager GUI tests, dialog construction, schema, compileall, local build, and diff checks pass. Manual persistence/keyboard checks remain.
- **Important warnings:** Preserve user files and backend behavior. Fix redesign-introduced regressions, but do not expand scope into existing bugs. Prior review findings remain recorded in T-001 and conversation.
- **Questions for user:** None.

---

## 14. Final Response Contract
At the end of each work session, briefly report: **Done**, **Verification**, **Remaining**, and **Next step**. Ensure the corresponding sections above are updated **before** responding. If unable to modify this file, say so explicitly and provide the exact updates needed.
