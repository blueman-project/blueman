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
- **Updated (UTC):** 2026-10-16
- **Branch / commit:** feature/redesign (see `git log` for current phase checkpoint)
- **Working tree:** T-008 dependency bootstrap is verified and ready for its checkpoint commit.
- **Active task:** T-008
- **Overall status:** Redesign takes priority over existing and future bug work. R1–R5 now include branding, themes, a responsive compatible shell, and opt-in real device cards synchronized to the legacy model.

## 8. Task Board
| ID | Priority | Status | Task / acceptance criteria | Notes |
| --- | --- | --- | --- | --- |
| T-001 | High | DONE | Review ARCHITECTURE_AUDIT.md, BUG_AUDIT.md, CLIXAD.md, and IMPLEMENTATION_PLAN.md against local code; report actionable inconsistencies. | Review only; no implementation authorized. |
| T-002 | High | DONE | Record redesign-first priority and remove bug-fix prerequisites from the implementation plan. | Existing bugs deferred until after Phases 1–8. |

| T-003 | High | DONE | Complete Phase 0 audit corrections, current baseline, upstream comparison, and actionable redesign plan. | Results and environmental limits are recorded in IMPLEMENTATION_PLAN.md. |
| T-004 | High | DONE | Deliver redesign slices R1–R4: generated brand identity, installable theme preferences/resources, then the compatible manager shell. | Checkpoint `38a180a5`; visual/hardware verification remains for hardening. |
| T-005 | High | DONE | R5 card/model selection bridge with real model data, targeted updates, filtering/removal handling, and legacy fallback. | Card preview is opt-in until action/menu compatibility passes in R6. |
| T-006 | High | TODO | R6 card actions and exclusive Connected/Paired/Available grouping while preserving plugin menu items. | Next phase; requires a phase checkpoint before work starts. |
| T-007 | High | DONE | Provide a repository-local build-and-run command that cannot replace the system Blueman installation. | Use `./blueman-next`; `./blueman` is occupied by the Python package directory. |
| T-008 | High | DONE | Make `./blueman-next` install missing build/runtime dependencies without installing Blueman itself. | Debian/Ubuntu apt bootstrap installs only missing packages; `--no-deps` opts out. |

## 9. Active Task Detail
- **Task ID:** T-008
- **Goal:** Bootstrap dependencies needed by the local build while preserving the non-installing application workflow.
- **Acceptance criteria:** On Debian/Ubuntu, detect missing packages and install only those through apt/sudo; support opting out; never invoke Meson/Ninja install or replace the distribution Blueman package.
- **Relevant files:** `blueman-next`, `tools/run-local-manager.py`, `docs/LOCAL_BUILD.md`.
- **Changes made:** Added fixed apt package detection/bootstrap derived from Ubuntu CI and a `--no-deps` escape hatch; updated local-build documentation.
- **Verification:** Shell/Python syntax, help output, mocked missing-package apt/sudo installation, mocked build completion, diff checks, and no-application-install audit pass. The real path correctly detected only `gettext`, `cython3`, `python-gi-dev`, and `libbluetooth-dev`, then stopped at the interactive sudo password prompt available only to the user.
- **Blockers / risks:** The user must enter their sudo password on the next local run; after that the same command resumes configuration/build automatically.
- **Next action:** Commit T-008, then have the user run `./blueman-next` interactively before R6/T-006 begins.

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

## 13. Handoff — READ THIS FIRST WHEN RESUMING
- **Last agent/session:** Codex, 2026-10-15
- **What was requested:** Do the redesign before fixing any existing bug.
- **What is done:** R1–R5 are committed. T-007/T-008 add a non-installing `./blueman-next` workflow with automatic Debian/Ubuntu dependency bootstrap.
- **What remains:** R6–R7 card actions/search/telemetry, later redesign phases, then deferred bug fixes. Generate Python/CSS palettes from one input rather than maintaining mirrored values.
- **Exact next step:** User runs `./blueman-next` and enters the sudo password; after successful launch, begin R6 card actions.
- **Files touched:** `blueman-next`, `docs/LOCAL_BUILD.md`, and `INSTRUCTIONS.md`.
- **Checks run and results:** Syntax/help, mocked missing-package installation/build, diff, and no-install audit pass. Real execution detected four missing packages and reached sudo authentication; no credentials were entered or recorded.
- **Important warnings:** Preserve user files and backend behavior. Fix redesign-introduced regressions, but do not expand scope into existing bugs. Prior review findings remain recorded in T-001 and conversation.
- **Questions for user:** None.

---

## 14. Final Response Contract
At the end of each work session, briefly report: **Done**, **Verification**, **Remaining**, and **Next step**. Ensure the corresponding sections above are updated **before** responding. If unable to modify this file, say so explicitly and provide the exact updates needed.
